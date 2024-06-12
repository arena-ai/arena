from typing import Any
from abc import ABC, abstractmethod
import os
import logging
import time
from dataclasses import dataclass, asdict
import json
import boto3
from fabric import Connection

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
    region: str = 'eu-north-1'
    instance_type: str ='g5.2xlarge'
    image: str = 'ami-0d47c2063be189fce'
    key: str = '~/.ssh/aws'

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

class Infra:
    def __init__(self):
        self._params = None
        self._state = None
        self.client = boto3.client('ec2', region_name=self.params.region)
        self.tags = lambda name: [{'Key': 'App', 'Value': 'arena'}, {'Key': 'Name', 'Value': f'arena-{name}'}]
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
        # Define the parameters for the instance
        instance_params = {
            'ImageId': self.params.image,  # replace with your desired AMI ID
            'InstanceType': self.params.instance_type,  # instance with GPU
            'MinCount': 1,
            'MaxCount': 1,
            'KeyName': self.params.key_pair_name,  # replace with your key pair name
            'SecurityGroupIds': [self.state.security_group_id],
            'InstanceInitiatedShutdownBehavior': 'terminate',  # instance terminates on shutdown
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': self.tags(self.params.instance_name)
                }
            ]
        }
        # Create the instance
        try:
            instances = self.client.run_instances(**instance_params)
            self.state.instance_id = instances['Instances'][0]['InstanceId']
            logging.info(f"Created instance: {self.instance['InstanceId']}")
        except Exception as e:
            logging.error(e)
    
    def wait_for_instance_ip(self):
        while 'PublicIpAddress' not in self.instance:
            logging.info('Waiting for IP...')
            time.sleep(1)
    
    def wait_until_running(self):
        # TODO change that
        while self.instance['State']['Name'] != 'running':
            logging.info(f'Waiting for "running" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)
    
    def wait_until_ready(self):
        # TODO change that
        while self.instance['State']['Name'] != 'running':
            logging.info(f'Waiting for "running" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)

    def wait_until_terminated(self):
        # TODO change that
        while self.instance['State']['Name'] != 'terminated':
            logging.info(f'Waiting for "terminated" state (Current state is "{self.instance["State"]["Name"]}")...')
            time.sleep(1)

    def push_git_key(self, private_key_path: str):
        private_key_path = os.path.expanduser(private_key_path)
        print(private_key_path)
        Connection(
            host=self.instance['PublicDnsName'],
            user='ubuntu',
            connect_kwargs={
                'key_filename': os.path.expanduser(self.params.key),
            },
            ).put(private_key_path, remote='/home/ubuntu/.ssh/id_rsa')
    
    def terminate(self):
        self.client.terminate_instances(InstanceIds=[self.state.instance_id])
        self.wait_until_terminated()
        self.state.instance_id = None
        self.client.delete_key_pair(KeyPairId=self.state.key_pair_id)
        self.state.key_pair_id = None
        self.client.delete_security_group(GroupId=self.state.security_group_id)
        self.state.security_group_id = None
        self.state.dump()

if __name__ == '__main__':
    infra = Infra()
    # infra.wait_until_running()
    # print(json.dumps(infra.instance, indent=2, default=str))
    # infra.push_git_key('~/.ssh/id_rsa')
    # print(json.dumps(infra.instance, indent=2, default=str))
    # print(f"{infra.instance['PublicDnsName']} ({infra.instance['PublicIpAddress']})")
    infra.terminate()
