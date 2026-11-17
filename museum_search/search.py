"""Search with an optional "less of this" (negative) query.

Three ways to score a document d, with query vector q and negative vector n:

  score        cos(d, q) - w * cos(d, n)
  vector       cos(d, q' - w * n')   where q' and n' are q and n at length 1
  vector-raw   cos(d, q - w * n)     with q and n as they come out of the model

Subtracting vectors in an embedding space is a known technique
(the old "king - man + woman" word-vector examples are one case).
This file makes no claim that it is new.

A fact worth knowing: when q' and n' have length 1, "vector" and "score"
always give the same order. cos(d, q' - w*n') equals
(cos(d, q') - w*cos(d, n')) divided by the length of (q' - w*n'),
and that length is the same for every document.
"""

from . import vectors

METHODS = ("score", "vector", "vector-raw")


def build_index(model, records):
    """Embed every record once. Returns a list of k-dimension vectors."""
    return [model.embed(vectors.record_text(r)) for r in records]


def score_all(model, doc_vecs, query, negative="", weight=0.5, method="score"):
    """Return one score per document, in the same order as doc_vecs.

    Returns None when the query has no known word (nothing to search for).
    An empty negative, or one with no known word, changes nothing.
    """
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    q = model.embed(query)
    if not any(q):
        return None
    n = model.embed(negative) if negative and negative.strip() else []
    has_neg = bool(n) and any(n)

    if method == "score":
        if not has_neg:
            return [vectors.cosine(d, q) for d in doc_vecs]
        return [vectors.cosine(d, q) - weight * vectors.cosine(d, n)
                for d in doc_vecs]

    if not has_neg:
        # Nothing to subtract: same as plain search for every method.
        return [vectors.cosine(d, q) for d in doc_vecs]
    if method == "vector":
        q, n = vectors.normalize(q), vectors.normalize(n)
    v = [a - weight * b for a, b in zip(q, n)]
    # If v is all zeros (query equals negative and weight is 1), every
    # score is 0.0, because cosine() returns 0.0 for a zero vector.
    return [vectors.cosine(d, v) for d in doc_vecs]


def rank(scores, records):
    """Sort best first. Ties are broken by record id, so output is repeatable."""
    order = sorted(range(len(records)),
                   key=lambda i: (-scores[i], records[i]["id"]))
    return order


def search(model, records, doc_vecs, query, negative="", weight=0.5,
           method="score", limit=10):
    """Return a list of (record, score) pairs, best first. [] if nothing to search."""
    scores = score_all(model, doc_vecs, query, negative, weight, method)
    if scores is None:
        return []
    order = rank(scores, records)[:limit]
    return [(records[i], scores[i]) for i in order]
