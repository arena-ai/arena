import os
import logging
import time
import json
import boto3
from fabric import Connection

logging.basicConfig(level=logging.INFO)

class Infra:
    def __init__(self, name: str = 'arena', region: str = 'eu-north-1', instance_type='g5.2xlarge', image='ami-0d47c2063be189fce', key='~/.ssh/aws'):
        self.name = name
        self.region = region
        self.security_group_name = f'{self.name}-security-group'
        self.key_pair = f'{self.name}-key-pair'
        self.instance_name = f'{self.name}-gpu-instance'
        self.instance_type = instance_type
        self.image = image
        self.key = key
        self.client = boto3.client('ec2', region_name=self.region)
        self.tags = lambda name: [{'Key': 'App', 'Value': 'arena'}, {'Key': 'Name', 'Value': f'arena-{name}'}]
        self.security_group()
        self.authorize_ssh()
        self.public_key()
    
    def security_group(self):
        """Create a Security Group if not exist"""
        try:
            security_group = self.client.create_security_group(
                Description = 'The security group for Arena GPU tests',
                GroupName = self.security_group_name,
                TagSpecifications = [{
                    'ResourceType': 'security-group',
                    'Tags': self.tags('security-group'),
                }]
            )
            self.security_group_id = security_group['GroupId']
        except Exception as e:
            security_groups = self.client.describe_security_groups(GroupNames=[self.security_group_name])
            self.security_group_id = security_groups['SecurityGroups'][0]['GroupId']
            logging.warning(e)
    
    def authorize_ssh(self):
        """Authorize SSH access"""
        try:
            response = self.client.authorize_security_group_ingress(
                GroupId=self.security_group_id,
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

    def public_key(self):
        public_key_path = os.path.expanduser(f'{self.key}.pub')
        with open(public_key_path, 'rb') as file:
            public_key = file.read()
            print(public_key)
        try:
            self.client.import_key_pair(
                KeyName=self.key_pair,
                PublicKeyMaterial=public_key,
                TagSpecifications = [{
                    'ResourceType': 'key-pair',
                    'Tags': self.tags('key-pair'),
                }]
            )
        except Exception as e:
            logging.warning(e.response['Error']['Message'])
    
    def gpu_instance(self):
        # Define the parameters for the instance
        instance_params = {
            'ImageId': self.image,  # replace with your desired AMI ID
            'InstanceType': self.instance_type,  # instance with GPU
            'MinCount': 1,
            'MaxCount': 1,
            'KeyName': self.key_pair,  # replace with your key pair name
            'SecurityGroupIds': [self.security_group_id],
            'InstanceInitiatedShutdownBehavior': 'terminate',  # instance terminates on shutdown
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': self.tags(self.instance_name)
                }
            ]
        }
        # Create the instance
        try:
            instances = self.client.run_instances(**instance_params)
            self.instance = instances['Instances'][0]
            logging.info(f"Created instance: {self.instance['InstanceId']}")
            while 'PublicIpAddress' not in self.instance:
                logging.info('Instance:', self.instance)
                time.sleep(1)
                instances = self.client.describe_instances(InstanceIds=[self.instance['InstanceId']])
                self.instance = instances['Reservations'][0]['Instances'][0]
            return self.instance
        except Exception as e:
            logging.error(e)
    
    def push_git_key(self, private_key_path: str):
        private_key_path = os.path.expanduser(private_key_path)
        Connection(
            host=self.instance['PublicDnsName'],
            user='ubuntu',
            connect_kwargs={
                'key_filename': os.path.expanduser(private_key_path),
            },
            ).put(private_key_path, remote='/home/ubuntu/.ssh/id_rsa')
    

if __name__ == '__main__':
    infra = Infra()
    instance = infra.gpu_instance()
    infra.push_git_key('~/.ssh/id_rsa')
    with open('instance.json', 'w') as file:
        json.dump(instance, file, indent=2, sort_keys=True, default=str)
    print(f"{instance['PublicDnsName']} ({instance['PublicIpAddress']})")
