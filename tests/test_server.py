from fastapi.testclient import TestClient

from nlp_pipeline.server import app

client = TestClient(app)


def test_analyze():
    response = client.post(
        "tokenize",
        json={
            "content": "The quick brown fox is brown and quick.",
            "extra": {"identifier": "urn:test:sentence:1"},
        },
    )

    assert response.status_code == 200

    tokenized_chunk = response.json()

    response = client.post("analyze", json=tokenized_chunk)

    assert response.status_code == 200

    resp_body = response.json()

    brown = [t for t in resp_body["tokens"] if t["text"].startswith("brown")]

    assert brown[0]["identifier"] == "brown[1]"
    assert brown[1]["identifier"] == "brown[2]"
    assert brown[1]["words"][0]["lemma"] is not None


def test_tokenize():
    response = client.post(
        "tokenize",
        json={
            "content": "The quick brown fox is brown and quick.",
            "extra": {"identifier": "urn:test:sentence:1"},
        },
    )

    assert response.status_code == 200

    resp_body = response.json()

    assert len(resp_body["tokens"]) == 9


def test_tokenize_indexes_tokens():
    response = client.post(
        "tokenize",
        json={
            "content": "The quick brown fox is brown and quick.",
            "extra": {"identifier": "urn:test:sentence:1"},
        },
    )

    assert response.status_code == 200

    resp_body = response.json()

    brown = [t for t in resp_body["tokens"] if t["text"].startswith("brown")]

    assert brown[0]["identifier"] == "brown[1]"
    assert brown[1]["identifier"] == "brown[2]"


def test_tokenize_works_without_extra():
    response = client.post(
        "tokenize",
        json={"content": "The quick brown fox is brown and quick."},
    )

    assert response.status_code == 200
