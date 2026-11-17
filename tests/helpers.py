"""Shared set-up: build the model once for all test files."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from museum_search import data  # noqa: E402

_CACHE = {}


def built():
    """Return (records, model, doc_vecs). Built on first call only."""
    if "built" not in _CACHE:
        records = data.load_records()
        model, doc_vecs = data.build(records)
        _CACHE["built"] = (records, model, doc_vecs)
    return _CACHE["built"]
