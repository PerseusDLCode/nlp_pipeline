from typing import Any, Optional

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
    extra: Optional[dict[str, Any]] = None


class TokenizedChunk(BaseModel):
    content: str
    extra: dict[str, Any] | None
    lang: str
    tokens: list[TextToken]


@app.get("/")
def root():
    return {"message": "Hello, world"}


@app.post("/tokenize")
def post_tokenize(chunk: TokenizableChunk) -> TokenizedChunk:
    tokenized = pipeline.tokenize(chunk.content)

    token_counts = {}
    tokens: list[TextToken] = []

    for token in tokenized.iter_tokens():
        token_text = token.text.strip()
        count = token_counts.get(token_text, 0) + 1

        t: TextToken = TextToken(
            end_char=token.end_char,
            id=token.id,
            identifier=f"{token.text}[{count}]",
            start_char=token.start_char,
            text=token.text,
            whitespace=len(token.spaces_after) > 0,
        )

        token_counts[token_text] = count

        tokens.append(t)

    content: str = chunk.content
    lang: str = tokenized.lang

    return TokenizedChunk(
        content=content,
        extra=chunk.extra,
        lang=lang,
        tokens=tokens,
    )
