from typing import Any
from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime
import logging
import json
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logging.basicConfig(level=logging.INFO)

class Config:
    def __init__(self, config_path: str = '7B.yaml', default_config_path: str = 'default_config.yaml'):
        """The config is saved as a file according to: https://github.com/mistralai/mistral-finetune/blob/main/example/7B.yaml"""
        self._config = None
        self.config_path = config_path
        self.default_config_path = default_config_path
        self.set_config()
    
    @property
    def config(self) -> dict[str, Any]:
        if not self._config:
            self.set_config()
        return self._config


    def set_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config:
                self._config = load(config, Loader=Loader)
        else:
            if os.path.exists(self.default_config_path):
                with open(self.default_config_path, 'r') as default_config:
                    self._config = load(default_config, Loader=Loader)
            else:
                self._config = {}
            # Set the config elements
            self._config['wandb']['project'] = 'arena-tests'
            self._config['wandb']['run_name'] = f'run-{datetime.now()}'
            self._config['wandb']['key'] = os.getenv('244af66353d33d53b5cb4f28a2ed24a277acd69a')
            with open(self.config_path, 'w') as config:
                dump(self._config, config, Dumper=Dumper)
                


    def format(self, datum: dict[str, Any]) -> dict[str, Any]:
        return {"messages": [
            {"role": "system", "content": "Given a meter ID, you return a series of hourly consumptions given as a json string."},
            {"role": "user", "content": json.dumps({"item_id": datum["item_id"]})},
            {"role": "assistant", "content": json.dumps({"consumption": [round(1000*x)/1000 for x in datum["target"][:100]]})}
        ]}


if __name__ == "__main__":
    print("[red]Training set loaded[/red]")
    print(next(iter(Config().config['train'])))
    print("[red]Test set loaded[/red]")
    print(next(iter(Config().config['test'])))