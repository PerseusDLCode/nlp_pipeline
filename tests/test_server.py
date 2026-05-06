from fastapi.testclient import TestClient

from nlp_pipeline.server import app

client = TestClient(app)


def test_tokenize():
    response = client.post(
        "tokenize",
        json={
            "content": "The quick brown fox is brown and quick.",
            "identifier": "urn:test:sentence:1",
        },
    )

    assert response.status_code == 200

    resp_body = response.json()

    assert len(resp_body["tokens"]) == 9
