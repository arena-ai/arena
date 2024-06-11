import os
import logging
import time
import json
import boto3

logging.basicConfig(level=logging.INFO)

class Infra:
    def __init__(self, name: str = 'arena', region: str = 'eu-north-1', instance_type='g5.2xlarge', image='ami-03dc624a6bfdafc83'):
        self.name = name
        self.region = region
        self.key_pair = f'{self.name}-key-pair'
        self.instance_name = f'{self.name}-gpu-instance'
        self.instance_type = instance_type
        self.image = image
        self.client = boto3.client('ec2', region_name=self.region)
    
    def public_key(self, public_key_path: str):
        public_key_path = os.path.expanduser(public_key_path)
        with open(public_key_path, 'rb') as file:
            public_key = file.read()
        try:
            self.client.import_key_pair(
                KeyName=self.key_pair,
                PublicKeyMaterial=public_key
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
            'InstanceInitiatedShutdownBehavior': 'terminate',  # instance terminates on shutdown
            'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': self.instance_name  # Replace with your desired instance name
                    }
                ]
            }
    ]
        }
        # Create the instance
        try:
            instances = self.client.run_instances(**instance_params)
            instance = instances['Instances'][0]
            logging.info(f"Created instance: {instance['InstanceId']}")
            while 'PublicIpAddress' not in instance:
                logging.info('Instance:', instance)
                time.sleep(1)
                instances = self.client.describe_instances(InstanceIds=[instance['InstanceId']])
                instance = instances['Reservations'][0]['Instances'][0]
            return instance
        except Exception as e:
            logging.error(e)

    

if __name__ == '__main__':
    infra = Infra()
    infra.public_key('~/.ssh/id_rsa.pub')
    instance = infra.gpu_instance()
    with open('instance.json', 'w') as file:
        json.dump(instance, file, indent=2, sort_keys=True, default=str)
    print(f"{instance['PublicDnsName']} ({instance['PublicIpAddress']})")