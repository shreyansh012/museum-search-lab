import unittest

from tests import helpers
from museum_search import data, vectors


class TokenizeTests(unittest.TestCase):
    def test_lowercase_accents_and_plurals(self):
        self.assertEqual(vectors.tokenize("Café Swords"), ["cafe", "sword"])

    def test_common_words_and_short_words_dropped(self):
        self.assertEqual(vectors.tokenize("The sword of a king"), ["sword", "king"])

    def test_double_s_kept(self):
        self.assertEqual(vectors.tokenize("dress"), ["dress"])

    def test_empty_and_none(self):
        self.assertEqual(vectors.tokenize(""), [])
        self.assertEqual(vectors.tokenize(None), [])


class MathTests(unittest.TestCase):
    def test_cosine_of_zero_vector_is_zero(self):
        self.assertEqual(vectors.cosine([0.0, 0.0], [1.0, 2.0]), 0.0)

    def test_cosine_basic(self):
        self.assertAlmostEqual(vectors.cosine([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(vectors.cosine([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_normalize_zero_stays_zero(self):
        self.assertEqual(vectors.normalize([0.0, 0.0]), [0.0, 0.0])


class FitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.model, cls.doc_vecs = helpers.built()

    def test_fit_is_deterministic(self):
        texts = [vectors.record_text(r) for r in self.records]
        again = vectors.fit(texts)
        self.assertEqual(again.terms, self.model.terms)
        self.assertEqual(again.idf, self.model.idf)
        self.assertEqual(again.comps, self.model.comps)

    def test_different_seed_gives_similar_cosines(self):
        # A different seed may rotate the raw numbers. The geometry
        # (cosines between texts) should stay close.
        texts = [vectors.record_text(r) for r in self.records]
        other = vectors.fit(texts, seed=99)
        a = vectors.cosine(self.model.embed("gold ring"), self.model.embed("silver ring"))
        b = vectors.cosine(other.embed("gold ring"), other.embed("silver ring"))
        self.assertAlmostEqual(a, b, delta=0.05)

    def test_columns_are_orthonormal(self):
        k = self.model.k
        for a in range(0, k, 7):
            for b in range(a, k, 5):
                col_a = [row[a] for row in self.model.comps]
                col_b = [row[b] for row in self.model.comps]
                want = 1.0 if a == b else 0.0
                self.assertAlmostEqual(vectors.dot(col_a, col_b), want, places=6)

    def test_unknown_text_embeds_to_zero(self):
        self.assertFalse(any(self.model.embed("zzzunknown")))

    def test_model_dict_round_trip(self):
        copy = vectors.Model.from_dict(self.model.to_dict())
        self.assertEqual(copy.terms, self.model.terms)
        a, b = self.model.embed("silk dress"), copy.embed("silk dress")
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, delta=1e-4)


class SampleDataTests(unittest.TestCase):
    def test_sample_file_is_sane(self):
        records = data.load_records()
        self.assertGreaterEqual(len(records), 200)
        ids = [r["id"] for r in records]
        self.assertEqual(len(ids), len(set(ids)))
        for r in records:
            for key in ("id", "title", "type", "culture", "medium", "tags",
                        "department", "url"):
                self.assertIn(key, r)
            self.assertIsInstance(r["tags"], list)


if __name__ == "__main__":
    unittest.main()
