import unittest

from tests import helpers
from museum_search import data, search, vectors


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.model, cls.doc_vecs = helpers.built()
        cls.by_id = {r["id"]: r for r in cls.records}

    def run_search(self, q, neg="", w=0.5, method="score", limit=10):
        return search.search(self.model, self.records, self.doc_vecs,
                             q, neg, w, method, limit)

    def rank_positions(self, q, neg, w, method):
        scores = search.score_all(self.model, self.doc_vecs, q, neg, w, method)
        order = search.rank(scores, self.records)
        return {self.records[i]["id"]: pos for pos, i in enumerate(order)}

    def has_word(self, rec, word):
        return word in vectors.tokenize(vectors.record_text(rec))

    # ---- determinism -------------------------------------------------------

    def test_same_search_twice_gives_same_results(self):
        for method in search.METHODS:
            a = self.run_search("silk", "dress", 0.7, method)
            b = self.run_search("silk", "dress", 0.7, method)
            self.assertEqual([(r["id"], s) for r, s in a],
                             [(r["id"], s) for r, s in b])

    def test_ties_break_by_id(self):
        scores = [1.0, 1.0, 0.5]
        recs = [{"id": 30}, {"id": 10}, {"id": 20}]
        self.assertEqual(search.rank(scores, recs), [1, 0, 2])

    def test_fresh_build_gives_same_results(self):
        model, doc_vecs = data.build(self.records)
        a = search.search(model, self.records, doc_vecs, "glass", "vase", 0.5, "score", 10)
        b = self.run_search("glass", "vase", 0.5, "score")
        self.assertEqual([r["id"] for r, _ in a], [r["id"] for r, _ in b])

    # ---- the negative term lowers the rank --------------------------------

    def test_negative_lowers_rank_of_matching_record(self):
        for method in search.METHODS:
            for q, neg in (("silk", "dress"), ("gold", "ring"), ("wood", "chair")):
                plain = self.rank_positions(q, "", 0, method)
                with_neg = self.rank_positions(q, neg, 0.5, method)
                first_ten = sorted(plain, key=plain.get)[:10]
                hits = [i for i in first_ten if self.has_word(self.by_id[i], neg)]
                self.assertTrue(hits, f"test needs a matching record for {q}/{neg}")
                best = hits[0]  # best-ranked record that contains the negative word
                self.assertGreater(with_neg[best], plain[best], (method, q, neg))

    def test_negative_words_leave_the_first_ten(self):
        plain = self.run_search("silk", "", 0)
        with_neg = self.run_search("silk", "dress", 1.0)

        def count(res):
            return sum(self.has_word(r, "dress") for r, _ in res)

        self.assertGreater(count(plain), 0)
        self.assertLess(count(with_neg), count(plain))

    def test_score_and_vector_give_same_order(self):
        for q, neg, w in (("silk", "dress", 0.5), ("glass", "vase", 2.0)):
            a = search.score_all(self.model, self.doc_vecs, q, neg, w, "score")
            b = search.score_all(self.model, self.doc_vecs, q, neg, w, "vector")
            order = search.rank(a, self.records)
            for x, y in zip(order, order[1:]):
                self.assertLessEqual(b[y], b[x] + 1e-9)

    # ---- empty and odd negatives ------------------------------------------

    def test_empty_negative_equals_plain_search(self):
        plain = search.score_all(self.model, self.doc_vecs, "gold", "", 0.5, "score")
        for method in search.METHODS:
            for neg in ("", "   ", "\t\n", None, "zzzunknown", "the of"):
                got = search.score_all(self.model, self.doc_vecs, "gold", neg, 0.5, method)
                self.assertEqual(got, plain, (method, repr(neg)))

    def test_empty_negative_search_results_match(self):
        a = self.run_search("gold", "")
        b = self.run_search("gold", "   ", 2.0, "vector")
        self.assertEqual([r["id"] for r, _ in a], [r["id"] for r, _ in b])

    def test_unknown_query_returns_nothing(self):
        self.assertEqual(self.run_search("zzzunknown"), [])
        self.assertEqual(self.run_search("", "dress"), [])
        self.assertEqual(self.run_search("   "), [])

    def test_negative_equal_to_query_at_weight_one_gives_zero_scores(self):
        scores = search.score_all(self.model, self.doc_vecs, "gold", "gold", 1.0, "vector")
        self.assertTrue(all(s == 0.0 for s in scores))

    def test_bad_method_raises(self):
        with self.assertRaises(ValueError):
            search.score_all(self.model, self.doc_vecs, "gold", "", 0.5, "nope")

    def test_limit_is_respected(self):
        self.assertEqual(len(self.run_search("gold", limit=3)), 3)


if __name__ == "__main__":
    unittest.main()
