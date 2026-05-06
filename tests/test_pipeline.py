from nlp_pipeline.pipeline import NLPPipeline


class TestPipeline:
    def test_tokenize_identifies_language(self):
        pipeline = NLPPipeline()

        doc1 = pipeline.tokenize("The fox is quick and brown.")

        assert doc1.lang == "en"

        doc2 = pipeline.tokenize("μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος")

        assert doc2.lang == "grc"
