# Perseus Digital Library – Code – NLP Pipeline

This project serves as a standalone NLP pipeline for the Perseus Digital Library.
It implements an HTTP API for tokenizing and analyzing chunks of text.

The API will assign identifiers to each token that are unique by chunk:
`{token}[{1-based index}]`. It is up to the service using the API to
ensure that these identifiers are globally unique for its purposes.

## Using/developing locally

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

### Using the HTTP API

To run the server locally, clone this repository, `cd` into the cloned
directory, and run

```sh
uv sync
uv run fastapi dev
```

Note that while the server is running, you can access interactive documentation
at `/docs`.

### Using the module directly

You can also import the `NLPPipeline` class from `nlp_pipeline.pipeline` and
call it directly, without needing to go through the HTTP API.

```python
from nlp_pipeline.pipeline import NLPPipeline

pipeline = NLPPipeline()

tokenized = pipeline.tokenize("The quick brown fox is brown and quick.")
analyzed = pipeline.analyze(tokenized)
```

### Testing

Tests are handled by `pytest`. After activating the virtual environment
(which `uv` should create when you call `uv sync`), just run

```sh
pytest
```

## LICENSE

MIT License

Copyright (c) 2026 The Perseus Digital Library

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
