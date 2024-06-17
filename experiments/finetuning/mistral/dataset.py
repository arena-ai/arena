from typing import Any
from abc import ABC, abstractmethod
from collections.abc import Iterator
import logging
import json
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()
from datasets import load_dataset


logging.basicConfig(level=logging.INFO)

class Dataset:
    def __init__(self, home: str, train_path: str = 'mistral_finetuning_train.jsonl', test_path: str = 'mistral_finetuning_test.jsonl'):
        self._data = None
        self.home = home
        self.train_path = train_path
        self.test_path = test_path
        self.wandb_key = os.getenv('WANDB_API_TOKEN')
        self.set_data()
    
    @property
    def data(self) -> dict[str, Iterator[dict[str, Any]]]:
        if not self._data:
            self.set_data()
        return {
            'train': self._data['train'](),
            'test': self._data['test'](),
        }

    def set_data(self):
        # Download the data if necessary
        if not os.path.exists(self.train_path) or not os.path.exists(self.test_path):
            dataset = load_dataset('LeoTungAnh/electricity_hourly')
            with open(self.train_path, 'w') as file:
                for datum in dataset['train']:
                    file.write(json.dumps(self.format(datum))+'\n')
            with open(self.test_path, 'w') as file:
                for datum in dataset['test']:
                    file.write(json.dumps(self.format(datum))+'\n')
        # Create the iterators
        def train():
            with open(f'{self.home}/{self.train_path}', 'r') as file:
                for row in file:
                    yield json.loads(row)
        def test():
            with open(f'{self.home}/{self.test_path}', 'r') as file:
                for row in file:
                    yield json.loads(row)
        # Assign the iterators to 
        self._data = {
            'train': train,
            'test': test,
        }

    def format(self, datum: dict[str, Any]) -> dict[str, Any]:
        return {"messages": [
            {"role": "system", "content": "Given a meter ID, you return a series of hourly consumptions given as a json string."},
            {"role": "user", "content": json.dumps({"item_id": datum["item_id"]})},
            {"role": "assistant", "content": json.dumps({"consumption": [round(1000*x)/1000 for x in datum["target"][:100]]})}
        ]}


if __name__ == "__main__":
    print("[red]Training set loaded[/red]")
    print(next(iter(Dataset().data['train'])))
    print("[red]Test set loaded[/red]")
    print(next(iter(Dataset().data['test'])))