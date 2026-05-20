import stanza

from stanza.models.common.doc import Token
from stanza.pipeline.multilingual import MultilingualPipeline

from nlp_pipeline.types import TextToken, TokenizableChunk, TokenizedChunk, TextWord

LANG_CONFIGS = {
    "la": {"package": "perseus", "processors": "tokenize,mwt,pos,lemma"},
    "grc": {"package": "perseus"},
}

TOKENIZER_LANG_CONFIGS = {
    "ar": {"processors": "tokenize"},
    "de": {"processors": "tokenize"},
    "en": {"processors": "tokenize"},
    "es": {"processors": "tokenize"},
    "fa": {"processors": "tokenize"},
    "fr": {"processors": "tokenize"},
    "grc": {"package": "perseus", "processors": "tokenize"},
    "he": {"processors": "tokenize"},
    "it": {"processors": "tokenize"},
    "la": {"package": "perseus", "processors": "tokenize"},
    "pt": {"processors": "tokenize"},
}

LANG_ID_CONFIG = {
    "langid_lang_subset": [
        "ar",
        "de",
        "en",
        "es",
        "fa",
        "fr",
        "grc",
        "he",
        "it",
        "la",
        "pt",
    ]
}


def token_identifier(token: Token, count: int):
    return f"{token.text.strip()}[{count}]"


def _build_token(token: Token, identifier: str) -> TextToken:
    words = [
        TextWord(
            id=word.id,
            deprel=word.deprel,
            deps=word.deps,
            feats=word.feats,
            head=word.head,
            lemma=word.lemma,
            misc=word.misc,
            text=word.text,
            upos=word.upos,
            xpos=word.xpos,
        )
        for word in token.words
    ]
    return TextToken(
        end_char=token.end_char,
        id=token.id,
        identifier=identifier,
        start_char=token.start_char,
        text=token.text,
        whitespace=len(token.spaces_after) > 0,
        words=words,
    )


def _collect_tokens(
    doc, pretokenized: list[TextToken] | None = None
) -> list[TextToken]:
    token_counts = {}
    tokens: list[TextToken] = []

    for token in doc.iter_tokens():
        token_text = token.text.strip()
        count = token_counts.get(token_text, 0) + 1
        identifier = token_identifier(token, count)
        t = _build_token(token, identifier)

        if pretokenized is not None:
            match = next((p for p in pretokenized if p.identifier == identifier), None)
            if match is not None:
                t.identifier = match.identifier
            else:
                print(f"No pretokenized match found for {token.to_dict()}.")

        token_counts[token_text] = count
        tokens.append(t)

    return tokens


class NLPPipeline:
    _nlp: MultilingualPipeline | None = None
    _tokenizer: MultilingualPipeline | None = None

    def __init__(self):
        self.nlp = NLPPipeline.get_nlp()
        self.tokenizer = NLPPipeline.get_tokenizer()

    @classmethod
    def get_nlp(cls, model_dir: str = "./stanza_models"):
        """TODO: (charles)
        Consider how we might accommodate code-switching. Stanza's
        "multilingual pipeline" is not, in fact, multilingual except
        insofar as it can *identify* multiple languages and call
        the appropriate model. We might need to train a model on
        both Greek and Latin.
        """

        if cls._nlp is None:
            cls._nlp = MultilingualPipeline(
                lang_id_config=LANG_ID_CONFIG,
                lang_configs=LANG_CONFIGS,
                model_dir=model_dir,
                download_method=stanza.DownloadMethod.REUSE_RESOURCES,
            )

        return cls._nlp

    @classmethod
    def get_tokenizer(cls, model_dir: str = "./stanza_models"):
        if cls._tokenizer is None:
            cls._tokenizer = MultilingualPipeline(
                lang_id_config=LANG_ID_CONFIG,
                lang_configs=TOKENIZER_LANG_CONFIGS,
                model_dir=model_dir,
                download_method=stanza.DownloadMethod.REUSE_RESOURCES,
            )

        return cls._tokenizer

    def analyze(self, chunk: TokenizedChunk) -> TokenizedChunk:
        chunk_str = "".join(
            t.text + (" " if t.whitespace else "") for t in chunk.tokens
        )
        nlped = self.nlp(chunk_str)

        return TokenizedChunk(
            content=chunk.content,
            extra=chunk.extra,
            lang=nlped.lang,
            tokens=_collect_tokens(nlped, pretokenized=chunk.tokens),
        )

    def analyze_str(self, s: str) -> TokenizedChunk:
        chunk = self.tokenize_str(s)

        return self.analyze(chunk)

    def tokenize(self, chunk: TokenizableChunk) -> TokenizedChunk:
        """Tokenize a citable chunk of text,
        adding a CTS URN to each token so that
        they can be reassembled properly later.
        This step is necessary for handling texts
        where sentences cross citation boundaries,
        such as in drama (where a sentence can
        span many lines) or philosophy (where
        sentences can span many of the columns
        or pages frequently used for citations).
        """

        tokenized = self.tokenizer(chunk.content)

        return TokenizedChunk(
            content=chunk.content,
            extra=chunk.extra,
            lang=tokenized.lang,
            tokens=_collect_tokens(tokenized),
        )

    def tokenize_str(self, s: str) -> TokenizedChunk:
        chunk = TokenizableChunk(content=s)

        return self.tokenize(chunk)
