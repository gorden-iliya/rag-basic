"""Single place for all Bedrock calls (chat + embeddings) so a provider swap is easy."""
import json
import os
from functools import lru_cache
from pathlib import Path

import boto3
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv()) or load_dotenv(Path(__file__).resolve().parent / ".env")

EMBEDDING_DIM = 1024

@lru_cache(maxsize=1)
def _client():
    return boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

def converse(messages, system_prompt, tool_config=None):
    """One Converse round-trip with the chat model; returns the raw response."""
    kwargs = {
        "modelId": os.environ["BEDROCK_MODEL_ID"],
        "messages": messages,
        "system": [{"text": system_prompt}],
        "inferenceConfig": {
            "maxTokens": int(os.getenv("MAX_TOKEN_PER_CALL", "4096")),
            "temperature": 0.0
        }
    }

    # Converse requires toolConfig on every call
    if tool_config:
        # toolChoice "auto" lets the model decide
        kwargs["toolConfig"] = {**tool_config, "toolChoice": {"auto": {}}}
    return _client().converse(**kwargs)

def embedding_model_id():
    return os.environ["BEDROCK_EMBEDDING_MODEL_ID"]

def embed(text, model_id=None):
    """Embed text into a unit-length 1024-d vector (Titan v2 request shape)."""
    body = {
        "inputText": text,
        "dimensions": EMBEDDING_DIM,
        # Unit-length vectors make FIASS inner product (IndextFlatIP) equal cosine similarity.
        "normalize": True
    }
    response = _client().invoke_model(
        modelId=model_id or embedding_model_id(),
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(response["body"].read())["embedding"]