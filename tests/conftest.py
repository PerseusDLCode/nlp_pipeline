from pathlib import Path

import pytest


@pytest.fixture
def test_tokenized_document():
    return (
        Path(__file__).resolve().parent
        / "fixtures"
        / "tlg0011.tlg001.perseus-grc2.tokenized.xml"
    )
