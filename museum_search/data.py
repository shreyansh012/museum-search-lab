"""Load the sample file and build the model from it."""

import json
import os

from . import search, vectors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_PATH = os.path.join(ROOT, "data", "sample.json")
MODEL_PATH = os.path.join(ROOT, "web", "model.json")


def load_records(path=SAMPLE_PATH):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build(records, **fit_args):
    """Return (model, doc_vecs) for a list of records."""
    model = vectors.fit([vectors.record_text(r) for r in records], **fit_args)
    return model, search.build_index(model, records)
