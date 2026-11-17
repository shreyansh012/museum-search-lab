"""Compare the three scoring methods on a few fixed (query, negative) pairs.

Run:  python -m museum_search experiment

Questions asked:
1. Do "score" and "vector" give the same order? (The algebra says yes.)
2. Where does "vector-raw" differ, and by how much?
3. Does the negative really push matching records out of the first 10?

The output is plain text (Markdown). Nothing here is random or timed,
so the same data gives the same report.
"""

from . import data, search, vectors

PAIRS = [
    ("gold", "ring"),
    ("silk", "dress"),
    ("glass", "vase"),
    ("wood", "chair"),
    ("bronze", "sculpture"),
    ("iran", "bowl"),
    ("italian", "armor"),
    ("ceramic", "bowl"),
]
WEIGHTS = [0.25, 0.5, 1.0, 2.0]
N = 10  # size of the "first N" window


def consistent_order(order, scores, tol=1e-9):
    """True if listing records in `order` never goes up in `scores` (within tol)."""
    return all(scores[b] <= scores[a] + tol for a, b in zip(order, order[1:]))


def overlap(order_a, order_b, n=N):
    return len(set(order_a[:n]) & set(order_b[:n]))


def has_word(record, word):
    return word in vectors.tokenize(vectors.record_text(record))


def count_literal(order, records, word, n=N):
    return sum(1 for i in order[:n] if has_word(records[i], word))


def run():
    records = data.load_records()
    model, doc_vecs = data.build(records)
    lines = []
    out = lines.append

    out("# Experiment report")
    out("")
    out(f"Records: {len(records)}. Vocabulary: {len(model.terms)} words. "
        f"Dimensions: {model.k}. Window: first {N} results.")
    out("")
    out("Methods: `score` = cos(d,q) - w*cos(d,n). `vector` = cos(d, q' - w*n') with "
        "q' and n' scaled to length 1. `vector-raw` = cos(d, q - w*n) with the "
        "vectors as the model gives them.")

    # ---- Part 1: score vs vector ------------------------------------------
    out("")
    out("## 1. `score` versus `vector`")
    out("")
    out("For each pair and weight: is the order the same, and how big is the "
        "largest gap between `vector` x |q' - w*n'| and `score`?")
    out("")
    out("| query | not | w | same order | max gap | score range | vector range |")
    out("|---|---|---|---|---|---|---|")
    same_all = True
    worst_gap = 0.0
    for q, n in PAIRS:
        if q not in model.index or n not in model.index:
            out(f"| {q} | {n} | - | skipped (word not in vocabulary) | | | |")
            continue
        qn = vectors.normalize(model.embed(q))
        nn = vectors.normalize(model.embed(n))
        for w in WEIGHTS:
            a = search.score_all(model, doc_vecs, q, n, w, "score")
            b = search.score_all(model, doc_vecs, q, n, w, "vector")
            length = vectors._norm([x - w * y for x, y in zip(qn, nn)])
            gap = max(abs(bi * length - ai) for ai, bi in zip(a, b))
            order_a = search.rank(a, records)
            same = consistent_order(order_a, b)
            same_all &= same
            worst_gap = max(worst_gap, gap)
            out(f"| {q} | {n} | {w} | {'yes' if same else 'NO'} | {gap:.1e} | "
                f"{min(a):.2f} to {max(a):.2f} | {min(b):.2f} to {max(b):.2f} |")
    out("")
    out(f"All orders the same: {'yes' if same_all else 'NO'}. "
        f"Largest gap anywhere: {worst_gap:.1e}.")
    out("")
    out("Reading: the order is the same because cos(d, q' - w*n') equals "
        "(cos(d,q') - w*cos(d,n')) divided by one number that does not depend on d. "
        "The two methods differ only in the size of the scores, not in the ranking. "
        "At w = 2 the scores go below zero in both. That is expected, not a bug.")

    # ---- Part 2: raw vectors ----------------------------------------------
    out("")
    out("## 2. `vector-raw` versus `score`")
    out("")
    out(f"Overlap is how many of the first {N} results the two methods share "
        f"(10 means the same set). 'Literal' is how many of the first {N} "
        "records contain the negative word in their text.")
    out("")
    out("| query | not | w | overlap | literal: plain | literal: score | literal: raw |")
    out("|---|---|---|---|---|---|---|")
    overlaps = []
    for q, n in PAIRS:
        if q not in model.index or n not in model.index:
            continue
        plain = search.rank(search.score_all(model, doc_vecs, q, "", 0, "score"), records)
        for w in WEIGHTS:
            a = search.score_all(model, doc_vecs, q, n, w, "score")
            r = search.score_all(model, doc_vecs, q, n, w, "vector-raw")
            oa, orr = search.rank(a, records), search.rank(r, records)
            ov = overlap(oa, orr)
            overlaps.append(ov)
            out(f"| {q} | {n} | {w} | {ov} | {count_literal(plain, records, n)} | "
                f"{count_literal(oa, records, n)} | {count_literal(orr, records, n)} |")
    differ = sum(1 for o in overlaps if o < N)
    out("")
    out(f"`vector-raw` shares all {N} results with `score` in "
        f"{len(overlaps) - differ} of {len(overlaps)} runs. "
        f"It differs in {differ} runs. Lowest overlap: {min(overlaps)} of {N}.")
    out("")
    out("Reading: after the squeeze to a few dimensions, the query and negative "
        "vectors have different lengths. With raw vectors, cos(d, q - w*n) is the "
        "same as `score` with a changed weight w' = w * |n| / |q|. "
        "So the weight w does not mean the same thing for each pair. "
        "The next table checks this: does `vector-raw` at w give the same order "
        "as `score` at w'?")
    out("")
    out("| query | not | length ratio n/q | w | same order as score at w' |")
    out("|---|---|---|---|---|")
    equiv_all = True
    for q, n in PAIRS:
        if q not in model.index or n not in model.index:
            continue
        ratio = vectors._norm(model.embed(n)) / vectors._norm(model.embed(q))
        for w in WEIGHTS:
            r = search.score_all(model, doc_vecs, q, n, w, "vector-raw")
            a2 = search.score_all(model, doc_vecs, q, n, w * ratio, "score")
            ok = consistent_order(search.rank(a2, records), r)
            equiv_all &= ok
            out(f"| {q} | {n} | {ratio:.2f} | {w} | {'yes' if ok else 'NO'} |")
    out("")
    out(f"All the same: {'yes' if equiv_all else 'NO'}. "
        "So `vector-raw` is not a different ranking idea. It is `score` with a "
        "weight that moves with the length of the two vectors.")

    # ---- Part 3: one worked example ---------------------------------------
    q, n, w = "silk", "dress", 0.5
    out("")
    out(f"## 3. One example: `{q}`, less of `{n}`, w = {w}")
    for label, neg, method in [("plain (no negative)", "", "score"),
                               ("score", n, "score"),
                               ("vector-raw", n, "vector-raw")]:
        out("")
        out(f"{label}:")
        out("")
        res = search.search(model, records, doc_vecs, q, neg, w, method, 5)
        for pos, (rec, sc) in enumerate(res, 1):
            out(f"{pos}. {sc:.3f}  {rec['title']} ({rec['type']}, {rec['department']})")

    # ---- Part 4: edge cases ------------------------------------------------
    out("")
    out("## 4. Edge cases checked")
    base = search.score_all(model, doc_vecs, "gold", "", 0.5, "score")
    for neg in ("", "   ", "zzzunknown"):
        for method in search.METHODS:
            got = search.score_all(model, doc_vecs, "gold", neg, 0.5, method)
            assert got == base, (neg, method)
    out("")
    out("- An empty, blank or unknown-word negative gives exactly the plain scores, "
        "for all three methods.")
    zero = search.score_all(model, doc_vecs, "gold", "gold", 1.0, "vector")
    out(f"- Negative equal to the query with w = 1 gives a zero vector. "
        f"All scores are 0.0: {all(x == 0.0 for x in zero)}.")
    none = search.search(model, records, doc_vecs, "zzzunknown", "", 0.5, "score")
    out(f"- A query with no known word returns {len(none)} results.")

    # ---- Limits -----------------------------------------------------------
    out("")
    out("## Limits of this experiment")
    out("")
    out(f"- {len(records)} records and {len(PAIRS)} hand-picked pairs. "
        "This shows behaviour, not a general result.")
    out("- No human judged the results. 'Literal' counts only check one thing: "
        "whether the negative word still appears.")
    out("- With so few records, many of the first results are near-copies "
        "(same object type from the same department).")
    return "\n".join(lines)


if __name__ == "__main__":
    print(run())
