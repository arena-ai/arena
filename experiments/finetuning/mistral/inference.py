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
                    lora_path: str | None = None) -> None:
        self.home = Path(home)
        self.model_path = Path(home, model_path)
        if lora_path:
            self.lora_path = Path(home, lora_path)
        else:
            self.lora_path = None
    
    def generate(self) -> None:
        tokenizer = MistralTokenizer.from_file(str(self.model_path / "tokenizer.model.v3"))  # change to extracted tokenizer file
        model = Transformer.from_folder(str(self.model_path))  # change to extracted model dir
        if self.lora_path:
            model.load_lora(str(self.lora_path))

        with open(self.home / "out.jsonl", "w") as file:
            for i in range(400,600):
                completion_request = ChatCompletionRequest(temperature=1.0, messages=[
                        SystemMessage(content="Given a meter ID, you return a series of hourly consumptions given as a json string."),
                        UserMessage(content=dumps({"item_id": f"MT_{i:03d}"}))
                    ])
                tokens = tokenizer.encode_chat_completion(completion_request).tokens
                # Generate the tokens
                out_tokens, _ = generate([tokens], model, max_tokens=1024, temperature=1.0, eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id)
                result = tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])
                # Write the generated row
                file.write(result+"\n")
                print(f"REQUEST = {completion_request}\nRESULT = {result}\n")


@app.command()
def inference(home: str = '/home/ubuntu',
              model_path: str = 'mistral_models/7B_instruct/',
              lora_path: str | None = None):
    inference = Inference(home, model_path=model_path, lora_path=lora_path)
    inference.generate()


if __name__ == "__main__":
    app()