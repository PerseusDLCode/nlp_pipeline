import stanza

from lxml import etree

XML_NAMESPACE = "{http://www.w3.org/XML/1998/namespace}"


class TokenizedDocument:
    _nlp_pipelines = {}
    _nlp_processors = "tokenize,mwt,pos,lemma"

    def __init__(self, filename: str):
        self.analyzed_sentences = None
        self.filename = filename
        self.tree = etree.parse(self.filename)

        self.set_language()
        self.gather_sentences()

    @classmethod
    def get_pipeline(cls, language: str):
        pipeline = cls._nlp_pipelines.get(language)

        if pipeline is not None:
            return pipeline

        pipeline = stanza.Pipeline(
            language,
            processors=cls._nlp_processors,
            model_dir="./stanza_models",
            download_method=stanza.DownloadMethod.REUSE_RESOURCES,
            tokenize_pretokenized=True,
        )

        cls._nlp_pipelines[language] = pipeline

        return pipeline

    def analyze_sentences(self):
        if self.analyzed_sentences is not None:
            return self.analyzed_sentences

        pipeline = TokenizedDocument.get_pipeline(self.language)

        self.analyzed_sentences = pipeline(self.sentences)

        return self.analyzed_sentences

    def gather_sentences(self):
        self.sentences = []

        for sentence in self.tree.iterfind("tokens"):
            tokens = []

            for token in sentence.iterfind("token"):
                tokens.append(token.attrib.get("raw"))

            self.sentences.append(tokens)

        return self.sentences

    def set_language(self):
        lang = self.tree.getroot().attrib.get(f"{XML_NAMESPACE}lang")

        if lang is None:
            self.language = "en"
        else:
            self.language = lang
