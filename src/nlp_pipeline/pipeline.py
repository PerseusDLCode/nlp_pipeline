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

    def analyse(self, chunk: TokenizedChunk) -> TokenizedChunk:
        return self.analyze(chunk)

    def analyze(self, chunk: TokenizedChunk) -> TokenizedChunk:
        if type(chunk) is str:
            chunk = self.tokenize(chunk)

        chunk_str = ""

        for t in chunk.tokens:
            chunk_str += t.text

            if t.whitespace:
                chunk_str += " "

        nlped = self.nlp(chunk_str)
        token_counts = {}
        tokens: list[TextToken] = []

        for token in nlped.iter_tokens():
            token_text = token.text.strip()
            count = token_counts.get(token_text, 0) + 1
            identifier = token_identifier(token, count)
            pretokenized_match = next(
                (t for t in chunk.tokens if t.identifier == identifier), None
            )

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
            t: TextToken = TextToken(
                end_char=token.end_char,
                id=token.id,
                identifier=identifier,
                start_char=token.start_char,
                text=token.text,
                whitespace=len(token.spaces_after) > 0,
                words=words,
            )

            # For now, we just reassign the identifer.
            # It _should_ be the same as before, but
            # this way we can be sure to match up the results.
            if pretokenized_match is not None:
                t.identifier = pretokenized_match.identifier
            else:
                print(f"No pretokenized match found for {token.to_dict()}.")

            token_counts[token_text] = count

            tokens.append(t)

        content: str = chunk.content
        lang: str = nlped.lang

        return TokenizedChunk(
            content=content,
            extra=chunk.extra,
            lang=lang,
            tokens=tokens,
        )

    def tokenize(self, chunk: TokenizableChunk | str) -> TokenizedChunk:
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

        if type(chunk) is str:
            chunk = TokenizableChunk(content=chunk)

        tokenized = self.tokenizer(chunk.content)  # ty:ignore[unresolved-attribute]
        token_counts = {}
        tokens: list[TextToken] = []

        for token in tokenized.iter_tokens():
            token_text = token.text.strip()
            count = token_counts.get(token_text, 0) + 1
            identifier = token_identifier(token, count)

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

            t: TextToken = TextToken(
                end_char=token.end_char,
                id=token.id,
                identifier=identifier,
                start_char=token.start_char,
                text=token.text,
                whitespace=len(token.spaces_after) > 0,
                words=words,
            )

            token_counts[token_text] = count

            tokens.append(t)

        content: str = chunk.content  # ty:ignore[unresolved-attribute]
        lang: str = tokenized.lang

        return TokenizedChunk(
            content=content,
            extra=chunk.extra,  # ty:ignore[unresolved-attribute]
            lang=lang,
            tokens=tokens,
        )
