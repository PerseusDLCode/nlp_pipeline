from fastapi import FastAPI

from nlp_pipeline.pipeline import NLPPipeline
from nlp_pipeline.types import TokenizableChunk, TokenizedChunk

app = FastAPI()
pipeline = NLPPipeline()


@app.get("/")
def root():
    return {"message": "Hello, world"}


@app.post("/analyse")
@app.post("/analyze")
def post_analyze(chunk: TokenizedChunk) -> TokenizedChunk:
    return pipeline.analyze(chunk)


@app.post("/tokenize")
def post_tokenize(chunk: TokenizableChunk) -> TokenizedChunk:
    return pipeline.tokenize(chunk)
