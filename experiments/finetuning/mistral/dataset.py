from typing import Any
from abc import ABC, abstractmethod
import os
import logging
import time
from dataclasses import dataclass, asdict
import json
import typer
import boto3
from fabric import Connection
from rich import print
from dotenv import load_dotenv
load_dotenv()
from datasets import load_dataset


logging.basicConfig(level=logging.INFO)

class Dataset:
    train_path: str = 'mistral_finetuning_train.jsonl'
    test_path: str = 'mistral_finetuning_test.jsonl'
    output_path: str = 'mistral_output.jsonl'

    dataset = load_dataset("LeoTungAnh/electricity_hourly")

    