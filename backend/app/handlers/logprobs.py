from lark import Lark, Transformer, v_args, Tree, Token
from lark.tree import Meta
from pydantic import BaseModel
from typing import Any, Optional
import math
from app.lm.models.chat_completion import TokenLogprob

class HasProb(BaseModel):
    value: Any
    start: int
    end: int
    logprob: float
    prob: float

def map_characters_to_token_indices(extracted_data_token: list[TokenLogprob]) -> list[int]:
    """
    Maps each character in the JSON string output to its corresponding token index.
    
    Args:
    extracted_data_token : A list of `TokenLogprob` objects, where each object represents a token and its data (such as the logprobs)

    Returns:
    A list of integers where each position corresponds to a character in the concatenated JSON string,
    and the integer at each position is the index of the token responsible for generating that specific character in the JSON string.
    
    Example:
    --------
    Given `extracted_data_token = [TokenLogprob(token='{'), TokenLogprob(token='"key1"'), TokenLogprob(token=': '), TokenLogprob(token='"value1"'), TokenLogprob(token='}')]`
    the JSON output is : '{"key1": "value1"}' and the function will return the list [0, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]
    
    """

    json_output = "".join(token_data.token for token_data in extracted_data_token)
                    
    token_indices = [None] * len(json_output)
    current_char_pos = 0

    for token_idx, token_data in enumerate(extracted_data_token):
        token_text = token_data.token
        for char_pos in range(len(token_text)):
            token_indices[current_char_pos] = token_idx
            current_char_pos += 1

    return token_indices
    
# Define a grammar for JSON
json_grammar = r"""
    start: value

    ?value: object              #'?' is a Lark convention indicating that the rule can return the value directly instead of creating a separate parse tree node.
          | array
          | string
          | SIGNED_NUMBER -> number    #'-> number' specifies an alias for the rule 
          | "true"
          | "false"
          | "null"

    array  : "[" [value ("," value)*] "]"
    object : "{" [pair ("," pair)*] "}"
    pair   : key ":" value
    key    : ESCAPED_STRING

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

@v_args(meta=True) 
class Extractor(Transformer):
    def __init__(self, tokens: list[TokenLogprob], token_indices: list[int]):
        super().__init__()
        self.tokens = tokens
        self.token_indices = token_indices

    def _compute_logprob_sum(self, start: int, end: int) -> float:
        token_start = self.token_indices[start]
        token_end = self.token_indices[end]
        sum_logporb= sum(self.tokens[i].logprob for i in range(token_start, token_end))
        return sum_logporb
    
    def number(self, meta: Meta, children: list[Token]) -> HasProb:
        logprob_sum = self._compute_logprob_sum(meta.start_pos, meta.end_pos)
        prob=math.exp(logprob_sum)* 100
        return HasProb(value=float(children[0]), start=meta.start_pos, end=meta.end_pos, logprob=logprob_sum, prob=prob)

    def string(self, meta: Meta, children: list[Token]) -> HasProb:
        logprob_sum = self._compute_logprob_sum(meta.start_pos, meta.end_pos)
        prob=math.exp(logprob_sum)* 100
        return HasProb(value=children[0][1:-1], start=meta.start_pos, end=meta.end_pos, logprob=logprob_sum, prob=prob)

    def true(self, meta: Meta, children: list[Token]) -> HasProb:
        logprob_sum = self._compute_logprob_sum(meta.start_pos, meta.end_pos)
        prob=math.exp(logprob_sum)* 100
        return HasProb(value=True, start=meta.start_pos, end=meta.end_pos, logprob=logprob_sum, prob=prob)

    def false(self, meta: Meta, children: list[Token]) -> HasProb:
        logprob_sum = self._compute_logprob_sum(meta.start_pos, meta.end_pos)
        prob=math.exp(logprob_sum)* 100
        return HasProb(value=False, start=meta.start_pos, end=meta.end_pos, logprob=logprob_sum, prob=prob)

    def null(self, meta: Meta, children: list[Token]):
        return None
    
    def array(self, meta: Meta, children:list[dict[str, Any] | Any]) -> list[dict[str,Any] | Any]:
        return [child.value if isinstance(child, HasProb) else child for child in children]
    
    def object(self, meta: Meta, children:list[tuple[str,Any]]) -> dict[str,Any]:
        result = {}
        for key, value in children:
            if isinstance(value, HasProb):
                result[key]=value.value
                result[f"{key}_logprob"]=value.logprob
                result[f"{key}_probability"]=value.prob
            else:
                result[key]=value
        return result
    
    def pair(self, meta: Meta, children:list[str, Any]) -> tuple[str, Any]:  
        value = children[1]
        key = children[0]
        if isinstance(value, Tree) and not value.children:    #['b', Tree(Token('RULE', 'value'), [])]
            value = None
        return key, value

    def key(self, meta: Meta, children: list[Token]) -> str:
        return children[0][1:-1]
    
    def start(self, meta: Meta, children:list[dict[str,Any]]) -> dict[str, Any]:
        return children[0]
    
json_parser = Lark(json_grammar, parser="lalr", propagate_positions=True, maybe_placeholders=False)

def extract_value_positions(json_string: str, tokens: list[TokenLogprob], token_indices: list[int]) -> dict[str,Any]:
    tree = json_parser.parse(json_string)
    extractor = Extractor(tokens, token_indices)
    return extractor.transform(tree)

