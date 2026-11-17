"""The browser code must give the same answers as the Python code.

The parity test is skipped when Node.js is not installed. No network is used.
"""

import json
import os
import shutil
import subprocess
import unittest

from tests import helpers
from museum_search import data, search, vectors

NODE = shutil.which("node")
CASES = [
    {"q": "silk", "neg": "dress", "w": 0.5, "method": "score"},
    {"q": "silk", "neg": "dress", "w": 0.5, "method": "vector"},
    {"q": "silk", "neg": "dress", "w": 0.5, "method": "vector-raw"},
    {"q": "gold ring", "neg": "", "w": 0.5, "method": "score"},
    {"q": "glass", "neg": "   ", "w": 1.0, "method": "vector"},
    {"q": "wood", "neg": "chair", "w": 2.0, "method": "score"},
    {"q": "Café SWORDS", "neg": "armor", "w": 0.3, "method": "vector-raw"},
    {"q": "zzzunknown", "neg": "dress", "w": 0.5, "method": "score"},
]


class ModelFileTests(unittest.TestCase):
    def test_model_file_matches_a_fresh_build(self):
        # The file the web page uses must not be out of date.
        _, model, _ = helpers.built()
        with open(data.MODEL_PATH, encoding="utf-8") as fh:
            saved = json.load(fh)
        self.assertEqual(saved["terms"], model.terms)
        self.assertEqual(saved["k"], model.k)
        self.assertEqual(len(saved["idf"]), len(model.idf))
        for a, b in zip(saved["idf"], model.idf):
            self.assertAlmostEqual(a, b, delta=1e-6)
        self.assertEqual(len(saved["comps"]), len(model.comps))
        for row_saved, row in zip(saved["comps"], model.comps):
            self.assertEqual(len(row_saved), len(row))
            for a, b in zip(row_saved, row):
                self.assertAlmostEqual(a, b, delta=1e-4)


@unittest.skipUnless(NODE, "node is not installed")
class WebParityTests(unittest.TestCase):
    def test_web_and_python_agree(self):
        records = data.load_records()
        with open(data.MODEL_PATH, encoding="utf-8") as fh:
            model = vectors.Model.from_dict(json.load(fh))
        doc_vecs = search.build_index(model, records)

        script = os.path.join(helpers.ROOT, "tests", "parity.js")
        proc = subprocess.run([NODE, script, json.dumps(CASES)],
                              capture_output=True, text=True, check=True, timeout=60)
        js_out = json.loads(proc.stdout)
        self.assertEqual(len(js_out), len(CASES))

        for case, js in zip(CASES, js_out):
            py = search.search(model, records, doc_vecs, case["q"], case["neg"],
                               case["w"], case["method"], 10)
            self.assertEqual(len(py), len(js), case)
            for pos, ((rec, score), (js_id, js_score)) in enumerate(zip(py, js)):
                self.assertAlmostEqual(score, js_score, delta=1e-9, msg=(case, pos))
                tied = any(abs(score - other) < 1e-9
                           for j, (_, other) in enumerate(js) if j != pos)
                if not tied:
                    self.assertEqual(rec["id"], js_id, (case, pos))


if __name__ == "__main__":
    unittest.main()
