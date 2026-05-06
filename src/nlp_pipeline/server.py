from fastapi import FastAPI

from nlp_pipeline.pipeline import NLPPipeline


app = FastAPI()
pipeline = NLPPipeline()


@app.get("/")
def root():
    return {"message": "Hello, world"}
