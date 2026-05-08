from typing import Any, Optional

from pydantic import BaseModel


class TextWord(BaseModel):
    id: int
    deprel: Optional[str]
    deps: Optional[str]
    feats: Optional[str]
    head: Optional[int]
    lemma: Optional[str]
    misc: Optional[str]
    text: Optional[str]
    upos: Optional[str]
    xpos: Optional[str]


class TextToken(BaseModel):
    end_char: int
    id: list[int]
    identifier: str
    misc: Optional[str] = None
    ner: Optional[str] = None
    start_char: int
    text: str
    whitespace: bool
    words: list[TextWord]


class TokenizableChunk(BaseModel):
    content: str
    extra: Optional[dict[str, Any]] = None


class TokenizedChunk(BaseModel):
    content: str
    extra: dict[str, Any] | None
    lang: str
    tokens: list[TextToken]
