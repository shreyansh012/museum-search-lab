"""Build word vectors and document vectors with the standard library only.

Steps:
1. Split text into words (tokenize).
2. Weight each word with TF-IDF.
3. Squeeze the big word space down to a few dimensions with a truncated SVD.
   The SVD here uses block power iteration (repeatedly multiply, then
   make the columns orthogonal again). It is a plain textbook method.

The same steps are written again in web/search.js so the browser page
gives the same answers. If you change the rules here, change them there.
"""

import math
import random
import re
import unicodedata

# Very common English words. They carry no meaning for search.
COMMON_WORDS = frozenset(
    "a an and are as at be by for from has in is it its of on or the to with "
    "this that these those was were which not no".split()
)

_WORD = re.compile(r"[a-z0-9]+")


def stem(word):
    """Tiny plural rule: 'swords' -> 'sword'. Leaves 'glass' alone."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text):
    """Lower-case, drop accents, split into words, drop common words."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    words = _WORD.findall(text.lower())
    out = []
    for w in words:
        w = stem(w)
        if len(w) >= 2 and w not in COMMON_WORDS:
            out.append(w)
    return out


def record_text(rec):
    """Join the searchable fields of one record into one string."""
    parts = [
        rec.get("title", ""),
        rec.get("type", ""),
        rec.get("culture", ""),
        rec.get("medium", ""),
        " ".join(rec.get("tags", [])),
        rec.get("department", ""),
    ]
    return " ".join(p for p in parts if p)


def _norm(vec):
    return math.sqrt(sum(x * x for x in vec))


def normalize(vec):
    """Scale to length 1. A zero vector stays a zero vector."""
    n = _norm(vec)
    if n == 0.0:
        return list(vec)
    return [x / n for x in vec]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    """Cosine of the angle between two vectors. 0.0 if either is zero."""
    na, nb = _norm(a), _norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)


class Model:
    """Vocabulary, word weights and the projection into k dimensions."""

    def __init__(self, terms, idf, comps):
        self.terms = terms          # sorted list of words
        self.idf = idf              # one weight per word
        self.comps = comps          # one row of k numbers per word
        self.k = len(comps[0]) if comps else 0
        self.index = {t: i for i, t in enumerate(terms)}

    # ----- save and load --------------------------------------------------

    def to_dict(self, decimals=6):
        """Plain dict for JSON. Numbers are rounded to keep the file small."""
        return {
            "k": self.k,
            "terms": self.terms,
            "idf": [round(x, decimals) for x in self.idf],
            "comps": [[round(x, decimals) for x in row] for row in self.comps],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["terms"], data["idf"], data["comps"])

    # ----- text to vector -------------------------------------------------

    def tfidf(self, text):
        """Sparse TF-IDF row as {word index: weight}, length 1. Unknown words are ignored."""
        counts = {}
        for w in tokenize(text):
            i = self.index.get(w)
            if i is not None:
                counts[i] = counts.get(i, 0) + 1
        row = {i: (1.0 + math.log(c)) * self.idf[i] for i, c in counts.items()}
        n = math.sqrt(sum(v * v for v in row.values()))
        if n == 0.0:
            return {}
        return {i: v / n for i, v in row.items()}

    def project(self, row):
        """Turn a sparse TF-IDF row into a k-dimension vector."""
        vec = [0.0] * self.k
        for i, w in row.items():
            comp = self.comps[i]
            for j in range(self.k):
                vec[j] += w * comp[j]
        return vec

    def embed(self, text):
        """Text to k-dimension vector. All zeros if no word is known."""
        return self.project(self.tfidf(text))

    def known_words(self, text):
        return [w for w in tokenize(text) if w in self.index]

    def unknown_words(self, text):
        return [w for w in tokenize(text) if w not in self.index]


def fit(texts, k=32, iterations=30, seed=7, min_df=2):
    """Learn the vocabulary, the weights and the k-dimension projection."""
    token_lists = [tokenize(t) for t in texts]
    df = {}
    for toks in token_lists:
        for w in set(toks):
            df[w] = df.get(w, 0) + 1
    terms = sorted(w for w, c in df.items() if c >= min_df)
    index = {t: i for i, t in enumerate(terms)}
    n_docs = len(texts)
    idf = [math.log((1.0 + n_docs) / (1.0 + df[t])) + 1.0 for t in terms]

    # Sparse TF-IDF matrix, one dict per document.
    rows = []
    for toks in token_lists:
        counts = {}
        for w in toks:
            i = index.get(w)
            if i is not None:
                counts[i] = counts.get(i, 0) + 1
        row = {i: (1.0 + math.log(c)) * idf[i] for i, c in counts.items()}
        n = math.sqrt(sum(v * v for v in row.values()))
        rows.append({i: v / n for i, v in row.items()} if n else {})

    n_terms = len(terms)
    k = max(1, min(k, n_terms, n_docs))
    q = _block_power_iteration(rows, n_terms, k, iterations, seed)
    comps = [[q[j][t] for j in range(k)] for t in range(n_terms)]
    return Model(terms, idf, comps)


def _block_power_iteration(rows, n_terms, k, iterations, seed):
    """Find k orthonormal directions that span the main directions of X.

    Repeat: Z = X^T (X Q), then make the columns of Z orthonormal.
    The result spans the leading k-dimension right singular space of X.
    Any rotation inside that space leaves dot products and cosines
    unchanged, so we do not need to sort out single vectors.
    """
    rng = random.Random(seed)
    q = [[rng.gauss(0.0, 1.0) for _ in range(n_terms)] for _ in range(k)]
    q = _orthonormalize(q)
    for _ in range(iterations):
        z = []
        for col in q:
            y = [sum(w * col[i] for i, w in row.items()) for row in rows]
            out = [0.0] * n_terms
            for yi, row in zip(y, rows):
                if yi:
                    for i, w in row.items():
                        out[i] += w * yi
            z.append(out)
        q = _orthonormalize(z)
    return q


def _orthonormalize(cols):
    """Modified Gram-Schmidt on a list of column vectors."""
    done = []
    for col in cols:
        v = list(col)
        for u in done:
            d = dot(v, u)
            v = [a - d * b for a, b in zip(v, u)]
        n = _norm(v)
        if n < 1e-12:
            v = [0.0] * len(v)
        else:
            v = [a / n for a in v]
        done.append(v)
    return done
