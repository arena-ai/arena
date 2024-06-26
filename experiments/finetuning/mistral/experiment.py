from typing import Any
from abc import ABC, abstractmethod
import os
import logging
import time
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import typer
import boto3
from fabric import Connection
from rich import print

from dataset import Dataset
from config import Config
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

class Persistent(ABC):
    persist_path: str

    def dump(self):
        with open(self.persist_path, 'w') as file:
            json.dump(asdict(self), file, indent=2, sort_keys=True, default=str)

    @classmethod
    def load(cls):
        with open(cls.persist_path, 'r') as file:
            return State(**json.load(file))

@dataclass
class Parameters(Persistent):
    persist_path: str = 'params.json'
    name: str = 'arena'
    # region: str = 'eu-west-1'
    region: str = 'eu-north-1'
    instance_type: str ='g5.12xlarge'
    image: str = 'ami-0d47c2063be189fce' # For eu-north-1
    # image: str = 'ami-0e1fae342f89b4159' # For eu-west-1
    key: str = '~/.ssh/aws'
    volume_size: int = 500

    @property
    def security_group_name(self) -> str:
        return f'{self.name}-security-group'

    @property
    def key_pair_name(self) -> str:
        return f'{self.name}-key-pair'
    
    @property
    def instance_name(self) -> str:
        return f'{self.name}-gpu-instance'

@dataclass
class State(Persistent):
    persist_path: str = 'state.json'
    security_group_id: str | None = None
    key_pair_id: str | None = None
    instance_id: str | None = None

class Experiment:
    def __init__(self, setup: bool = True):
        self._params = None
        self._state = None
        self.client = boto3.client('ec2', region_name=self.params.region)
        self.tags = lambda name: [{'Key': 'App', 'Value': 'arena'}, {'Key': 'Name', 'Value': name}]
        if setup:
            self.set_state()

    @property
    def params(self) -> Parameters:
        if not self._params:
            try:
                self._params = Parameters.load()
            except Exception as e:
                self._params = Parameters()
                self._params.dump()
        return self._params

    @property
    def state(self) -> State:
        if not self._state:
            try:
                self._state = State.load()
            except Exception as e:
                self._state = State()
        return self._state

    @property
    def security_group(self) -> dict[str, Any]:
        """Read the security-group information"""
        try:
            security_groups = self.client.describe_security_groups(GroupNames=[self.params.security_group_name])
            return security_groups['SecurityGroups'][0]
        except Exception as e:
            self.state.security_group_id = None
            self.set_state()

    @property
    def key_pair(self) -> dict[str, Any]:
        """Read the key-pair information"""
        try:
            key_pairs = self.client.describe_key_pairs(KeyPairIds=[self.state.key_pair_id])
            return key_pairs['KeyPairs'][0]
        except Exception as e:
            self.state.key_pair_id = None
            self.set_state()

    @property
    def instance(self) -> dict[str, Any]:
        """Read the instance information"""
        try:
            instances = self.client.describe_instances(InstanceIds=[self.state.instance_id])
            return instances['Reservations'][0]['Instances'][0]
        except Exception as e:
            self.state.instance_id = None
            self.set_state()

    @property
    def connection(self) -> Connection:
        return Connection(
            host=self.instance['PublicDnsName'],
            user='ubuntu',
            connect_kwargs={
                'key_filename': os.path.expanduser(self.params.key),
            },
        )
    
    def set_state(self):
        """The controller"""
        if not self.state.security_group_id:
            self.set_security_group()
        if not self.state.key_pair_id:
            self.set_key_pair()
        if not self.state.instance_id:
            self.set_instance()
        self.state.dump()

    def set_security_group(self):
        """Create a Security Group if not exist"""
        try:
            security_group = self.client.create_security_group(
                Description = 'The security group for Arena GPU tests',
                GroupName = self.params.security_group_name,
                TagSpecifications = [{
                    'ResourceType': 'security-group',
                    'Tags': self.tags('security-group'),
                }]
            )
            self.state.security_group_id = security_group['GroupId']
            self.set_authorize_ssh()
        except Exception as e:
            logging.warning(e)
            security_groups = self.client.describe_security_groups(GroupNames=[self.params.security_group_name])
            self.state.security_group_id = security_groups['SecurityGroups'][0]['GroupId']
    
    def set_authorize_ssh(self):
        """Authorize SSH access"""
        try:
            response = self.client.authorize_security_group_ingress(
                GroupId=self.state.security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{
                            'CidrIp': '0.0.0.0/0',  # Allows access from anywhere
                            'Description': 'Allow SSH from anywhere'
                        }]
                    }
                ]
            )
            logging.info(f"Ingress Successfully Set: {response}")
        except Exception as e:
            logging.warning(e)

    def set_key_pair(self):
        public_key_path = os.path.expanduser(f'{self.params.key}.pub')
        with open(public_key_path, 'rb') as file:
            public_key = file.read()
            print(public_key)
        try:
            key_pair = self.client.import_key_pair(
                KeyName=self.params.key_pair_name,
                PublicKeyMaterial=public_key,
                TagSpecifications = [{
                    'ResourceType': 'key-pair',
                    'Tags': self.tags('key-pair'),
                }]
            )
            self.state.key_pair_id = key_pair['KeyPairId']
        except Exception as e:
            logging.warning(e.response['Error']['Message'])
            key_pairs = self.client.describe_key_pairs(KeyNames=[self.params.key_pair_name])
            self.state.key_pair_id = key_pairs['KeyPairs'][0]['KeyPairId']
    
    def set_instance(self):
        # Create the instance
        try:
            instances = self.client.run_instances(
                ImageId = self.params.image,  # replace with your desired AMI ID
                InstanceType = self.params.instance_type,  # instance with GPU
                MinCount = 1,
                MaxCount = 1,
                KeyName = self.params.key_pair_name,  # replace with your key pair name
                SecurityGroupIds = [self.state.security_group_id],
                InstanceInitiatedShutdownBehavior = 'terminate',  # instance terminates on shutdown
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/sda1',  # Default root device name; may vary per AMI
                        'Ebs': {
                            'VolumeSize': self.params.volume_size, # size in GB
                            'DeleteOnTermination': True,
                        }
                    }
                ],
                TagSpecifications = [
                    {
                        'ResourceType': 'instance',
                        'Tags': self.tags(self.params.instance_name)
                    }
                ])
            self.state.instance_id = instances['Instances'][0]['InstanceId']
            logging.info(f"Created instance: {self.instance['InstanceId']}")
        except Exception as e:
            logging.error(e)
    
    def wait_for_instance_ip(self):
        while 'PublicIpAddress' not in self.instance:
            logging.info('Waiting for IP...')
            time.sleep(1)
    
    def wait_until_running(self):
        while 'State' not in self.instance or 'Name' not in self.instance['State'] or self.instance['State']['Name'] != 'running':
            logging.info(f'Waiting for "running" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)
    
    def wait_until_ready(self):
        while 'State' not in self.instance or 'Name' not in self.instance['State'] or self.instance['State']['Name'] != 'running':
            logging.info(f'Waiting for "running" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)

    def wait_until_terminated(self):
        while 'State' not in self.instance or 'Name' not in self.instance['State'] or self.instance['State']['Name'] != 'terminated':
            logging.info(f'Waiting for "terminated" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)
    
    def put(self, src_path: str, dest_path: str):
        src_path = os.path.expanduser(src_path)
        self.connection.put(src_path, remote=dest_path)
    
    def run(self, cmd: str):
        self.connection.run(cmd, pty=True)
        
    def put_key(self, private_key_path: str):
        self.put(private_key_path, '/home/ubuntu/.ssh/id_rsa')
    
    def terminate(self):
        self.client.terminate_instances(InstanceIds=[self.state.instance_id])
        self.wait_until_terminated()
        self.state.instance_id = None
        self.client.delete_key_pair(KeyPairId=self.state.key_pair_id)
        self.state.key_pair_id = None
        self.client.delete_security_group(GroupId=self.state.security_group_id)
        self.state.security_group_id = None
        self.state.dump()


app = typer.Typer()


@app.command()
def create():
    print(f"Creating a GPU instance")
    compute = Experiment()
    compute.wait_until_running()
    print(json.dumps(compute.instance, indent=2, default=str))
    print(f"{compute.instance['PublicDnsName']} ({compute.instance['PublicIpAddress']})")


@app.command()
def setup(home: str = '/home/ubuntu'):
    print(f"Push the setup script and run it")
    compute = Experiment()
    compute.wait_until_running()
    compute.put('.env', str(Path(home, '.env')))
    compute.put('setup.sh', str(Path(home, 'setup.sh')))
    compute.run(str(Path(home, 'setup.sh')))


@app.command()
def train(home: str = '/home/ubuntu'):
    print(f"Run a new training")
    compute = Experiment()
    compute.wait_until_running()
#     compute.connection.run("""cd ${HOME}/mistral-finetune
# export CUDA_VISIBLE_DEVICES="0"
# nohup ${HOME}/.local/bin/torchrun -m train ../7B_instruct.yaml > output.log 2>&1 & # Run the training in the background
# """, hide=True, pty=False)
    compute.connection.run("""cd ${HOME}/mistral-finetune
export CUDA_VISIBLE_DEVICES="0,1,2,3"
nohup ${HOME}/.local/bin/torchrun --nproc-per-node 4 --master_port $RANDOM -m train ../7B_instruct.yaml > output.log 2>&1 & # Run the training in the background
""", hide=True, pty=False)


@app.command()
def shell(cmd: str):
    compute = Experiment()
    compute.wait_until_running()
    compute.run(cmd)


@app.command()
def terminate():
    compute = Experiment(setup=False)
    if compute.state.instance_id:
        print(f"Terminating the instance")
        compute.terminate()
    else:
        print(f"Nothing to terminate")

TRAIN_PATH: str = 'mistral_finetuning_train.jsonl'
TEST_PATH: str = 'mistral_finetuning_test.jsonl'

@app.command()
def data(home: str = '/home/ubuntu'):
    dataset = Dataset(home, train_path=TRAIN_PATH, test_path=TEST_PATH)
    print(f"{len([d for d in dataset.data['train']])} rows loaded from the train set")
    print(f"{len([d for d in dataset.data['test']])} rows loaded from the test set")
    print("[green]Data loaded[/green]")


@app.command()
def config(home: str = '/home/ubuntu'):
    Config(home, train_path=TRAIN_PATH, test_path=TEST_PATH, wandb_key=os.getenv('WANDB_API_TOKEN'))
    print("[green]Config loaded[/green]")

    
@app.command()
def inference(home: str = '/home/ubuntu'):
    compute = Experiment()
    compute.wait_until_running()
    compute.run("""cd ${HOME}/arena/experiments/finetuning/mistral/
export RUN_PATH=$(awk '/run_dir:/ {print $2}' ${HOME}/7B_instruct.yaml)
export RUN_PATH=${HOME}/mistral_run-2024-06-21-15-39-53
export STEPS=$(awk '/max_steps:/ {printf "%06d", $2}' ${HOME}/7B_instruct.yaml)
python3 inference.py --model-path ${RUN_PATH}/checkpoints/checkpoint_${STEPS}/consolidated
""")


@app.command()
def analyze(data_path: str = 'mistral_finetuning_train.jsonl', output_path: str = 'out.jsonl'):
    train_data = []
    with open(data_path, "r") as f:
        for row in f:
            train_data.append(np.array(json.loads(json.loads(row)["messages"][-1]["content"])["consumption"]))

    # Plot a few trajectories
    plt.title("Some training data")
    for i in range(10):
        plt.plot(train_data[i])
    plt.show()

    synth_data = []
    with open(output_path, "r") as f:
        for row in f:
            synth_data.append(np.array(json.loads(row)['consumption']))
    
    # Plot a few synthetic trajectories
    plt.title("Synthetic data")
    for i in range(10):
        plt.plot(synth_data[i])
    plt.show()

    def closest(synthetic: np.ndarray, training: list[np.ndarray]) -> np.ndarray:
        current_closest = training[0]
        current_dist = np.sum(np.square(synthetic-current_closest))
        for training in training[1:]:
            dist = np.sum(np.square(synthetic-training))
            if dist < current_dist:
                current_closest = training
        return current_closest

    for synth in synth_data:
        try:
            close = closest(synth[:100], train_data)
            if np.std(close) > 0.1:
                plt.title("Closest series to a generated one")
                plt.ylim(-2, 6)
                plt.plot(synth)
                plt.plot(close)
                plt.show()
        except:
            pass
    
    stacked_train_data = np.vstack(train_data)
    mean_train = np.mean(stacked_train_data, axis=0)
    med_train = np.median(stacked_train_data, axis=0)
    perc90_train = np.percentile(stacked_train_data, 90, axis=0)
    perc10_train = np.percentile(stacked_train_data, 10, axis=0)

    stacked_synth_data = np.vstack([series[:100] for series in synth_data if len(series)>=100])
    mean_synth = np.mean(stacked_synth_data, axis=0)
    med_synth = np.median(stacked_synth_data, axis=0)
    perc90_synth = np.percentile(stacked_synth_data, 90, axis=0)
    perc10_synth = np.percentile(stacked_synth_data, 10, axis=0)

    plt.title("Compare means")
    plt.plot(mean_train, color="tab:blue")
    plt.plot(mean_synth, color="tab:orange")
    plt.show()

    plt.title("Compare percentiles")
    plt.plot(med_train, color="tab:blue", linewidth=2)
    plt.plot(med_synth, color="tab:orange", linewidth=2)
    plt.plot(perc90_train, color="tab:blue", linewidth=0.5)
    plt.plot(perc90_synth, color="tab:orange", linewidth=0.5)
    plt.plot(perc10_train, color="tab:blue", linewidth=0.5)
    plt.plot(perc10_synth, color="tab:orange", linewidth=0.5)
    plt.show()

    plt.title("Cross correlation (time 0 x time 24)")
    plt.plot(stacked_train_data[:, 0], stacked_train_data[:, 24], marker=".", color="tab:blue", linewidth=0)
    plt.plot(stacked_synth_data[:, 0], stacked_synth_data[:, 24], marker=".", color="tab:orange", linewidth=0)
    plt.show()


if __name__ == "__main__":
    app()