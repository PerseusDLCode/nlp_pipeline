from nlp_pipeline.base_text import TokenizedDocument


class TestBaseText:
    def test_parses_tokenized_document(self, test_tokenized_document):
        doc = TokenizedDocument(test_tokenized_document)

        assert len(doc.sentences) > 0

    def test_analyses_document_text(self, test_tokenized_document):
        doc = TokenizedDocument(test_tokenized_document)

        doc.analyse_sentences()

        assert len(doc.analysed_sentences.sentences) > 0
