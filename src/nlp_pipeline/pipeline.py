import stanza

from stanza.pipeline.multilingual import MultilingualPipeline

from stanza.models.common.doc import Token


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


def set_cts_urn(self, value: str):
    self._cts_urn = value


Token.add_property(
    "cts_urn", default=None, getter=lambda self: self._cts_urn, setter=set_cts_urn
)


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

    def process(self, document: str):
        return self.nlp(document)

    def tokenize(self, document: str):
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

        return self.tokenizer(document)
