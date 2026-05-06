from fastapi import FastAPI
from pydantic import BaseModel

from nlp_pipeline.pipeline import NLPPipeline


app = FastAPI()
pipeline = NLPPipeline()


class TextToken(BaseModel):
    end_char: int
    id: list[int]
    identifier: str
    start_char: int
    text: str
    whitespace: bool


class TokenizableChunk(BaseModel):
    content: str
    identifier: str


class TokenizedChunk(BaseModel):
    content: str
    identifier: str
    lang: str
    tokens: list[TextToken]


@app.get("/")
def root():
    return {"message": "Hello, world"}


@app.post("/tokenize")
def post_tokenize(chunk: TokenizableChunk):
    tokenized = pipeline.tokenize(chunk.content)

    token_counts = {}
    tokens = []

    for token in tokenized.iter_tokens():
        token_text = token.text.strip()
        count = token_counts.get(token_text, 0) + 1

        t = {
            "end_char": token.end_char,
            "id": token.id,
            "identifer": f"{chunk.identifier}@{token.text}[{count}]",
            "start_char": token.start_char,
            "text": token.text,
            "whitespace": len(token.spaces_after) > 0,
        }

        token_counts[token_text] = count

        tokens.append(t)

    return {
        "content": chunk.content,
        "identifier": chunk.identifier,
        "lang": tokenized.lang,
        "tokens": tokens,
    }
