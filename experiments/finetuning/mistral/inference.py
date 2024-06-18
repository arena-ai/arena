import os
from json import dumps, loads
from pathlib import Path
import typer

from mistral_inference.model import Transformer
from mistral_inference.generate import generate

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import SystemMessage, UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest

app = typer.Typer()

class Inference:
    def __init__(self, home: str,
                    model_path: str = 'mistral_models/7B_instruct/',
                    lora_path: str = 'mistral_run-2024-06-18-12-00-37/checkpoints/checkpoint_001000/consolidated/lora.safetensors') -> None:
        self.home = Path(home)
        self.model_path = Path(home, model_path)
        self.lora_path = Path(home, lora_path)
    
    def generate(self) -> None:
        tokenizer = MistralTokenizer.from_file(str(self.model_path / "tokenizer.model.v3"))  # change to extracted tokenizer file
        model = Transformer.from_folder(str(self.model_path))  # change to extracted model dir
        model.load_lora(str(self.lora_path))

        completion_request = ChatCompletionRequest(messages=[
                SystemMessage(content="Given a meter ID, you return a series of hourly consumptions given as a json string."),
                UserMessage(content=dumps({"item_id": "MT_130"}))
            ])

        tokens = tokenizer.encode_chat_completion(completion_request).tokens

        out_tokens, _ = generate([tokens], model, max_tokens=64, temperature=1.0, eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id)
        result = tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])

        print(result)


@app.command()
def inference(home: str = '/home/ubuntu',
              model_path: str = 'mistral_models/7B_instruct/',
              lora_path: str = 'mistral_run-2024-06-18-12-00-37/checkpoints/checkpoint_001000/consolidated/lora.safetensors'):
    inference = Inference(home, model_path=model_path, lora_path=lora_path)
    inference.generate()


if __name__ == "__main__":
    app()