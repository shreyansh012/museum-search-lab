// Search logic for the browser. Plain JavaScript, no build step.
// It repeats the rules in museum_search/vectors.py and museum_search/search.py.
// If you change a rule there, change it here too.
// The test tests/test_web_parity.py checks that both give the same answers.

(function (root) {
  "use strict";

  var COMMON_WORDS = new Set(
    ("a an and are as at be by for from has in is it its of on or the to with " +
     "this that these those was were which not no").split(" ")
  );

  function stem(word) {
    if (word.length > 3 && word.endsWith("s") && !word.endsWith("ss")) {
      return word.slice(0, -1);
    }
    return word;
  }

  function tokenize(text) {
    var t = (text || "").normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
    var words = t.match(/[a-z0-9]+/g) || [];
    var out = [];
    for (var i = 0; i < words.length; i++) {
      var w = stem(words[i]);
      if (w.length >= 2 && !COMMON_WORDS.has(w)) out.push(w);
    }
    return out;
  }

  function recordText(rec) {
    var parts = [rec.title, rec.type, rec.culture, rec.medium,
                 (rec.tags || []).join(" "), rec.department];
    return parts.filter(function (p) { return p; }).join(" ");
  }

  function norm(v) {
    var s = 0;
    for (var i = 0; i < v.length; i++) s += v[i] * v[i];
    return Math.sqrt(s);
  }

  function dot(a, b) {
    var s = 0;
    for (var i = 0; i < a.length; i++) s += a[i] * b[i];
    return s;
  }

  function cosine(a, b) {
    var na = norm(a), nb = norm(b);
    if (na === 0 || nb === 0) return 0;
    return dot(a, b) / (na * nb);
  }

  function normalize(v) {
    var n = norm(v);
    if (n === 0) return v.slice();
    return v.map(function (x) { return x / n; });
  }

  function isZero(v) {
    for (var i = 0; i < v.length; i++) if (v[i] !== 0) return false;
    return true;
  }

  // model = {k, terms, idf, comps} as written by `python -m museum_search export-web`
  function makeModel(raw) {
    var index = new Map();
    raw.terms.forEach(function (t, i) { index.set(t, i); });
    return { k: raw.k, terms: raw.terms, idf: raw.idf, comps: raw.comps, index: index };
  }

  function embed(model, text) {
    var counts = new Map();
    tokenize(text).forEach(function (w) {
      var i = model.index.get(w);
      if (i !== undefined) counts.set(i, (counts.get(i) || 0) + 1);
    });
    var vec = new Array(model.k).fill(0);
    if (counts.size === 0) return vec;
    var weights = [], sumSq = 0;
    counts.forEach(function (c, i) {
      var w = (1 + Math.log(c)) * model.idf[i];
      weights.push([i, w]);
      sumSq += w * w;
    });
    var n = Math.sqrt(sumSq);
    weights.forEach(function (p) {
      var w = p[1] / n, comp = model.comps[p[0]];
      for (var j = 0; j < model.k; j++) vec[j] += w * comp[j];
    });
    return vec;
  }

  function unknownWords(model, text) {
    return tokenize(text).filter(function (w) { return !model.index.has(w); });
  }

  function buildIndex(model, records) {
    return records.map(function (r) { return embed(model, recordText(r)); });
  }

  var METHODS = ["score", "vector", "vector-raw"];

  // One score per document, or null if the query has no known word.
  function scoreAll(model, docVecs, query, negative, weight, method) {
    if (METHODS.indexOf(method) < 0) throw new Error("bad method");
    var q = embed(model, query);
    if (isZero(q)) return null;
    var hasNeg = !!(negative && negative.trim());
    var n = hasNeg ? embed(model, negative) : null;
    if (n && isZero(n)) n = null;
    if (!n) return docVecs.map(function (d) { return cosine(d, q); });
    if (method === "score") {
      return docVecs.map(function (d) {
        return cosine(d, q) - weight * cosine(d, n);
      });
    }
    if (method === "vector") { q = normalize(q); n = normalize(n); }
    var v = q.map(function (x, i) { return x - weight * n[i]; });
    return docVecs.map(function (d) { return cosine(d, v); });
  }

  function rank(scores, records) {
    var order = records.map(function (_, i) { return i; });
    order.sort(function (a, b) {
      if (scores[b] !== scores[a]) return scores[b] - scores[a];
      return records[a].id - records[b].id;
    });
    return order;
  }

  function search(model, records, docVecs, query, negative, weight, method, limit) {
    var scores = scoreAll(model, docVecs, query, negative, weight, method);
    if (scores === null) return [];
    return rank(scores, records).slice(0, limit).map(function (i) {
      return { record: records[i], score: scores[i] };
    });
  }

  var api = {
    tokenize: tokenize, recordText: recordText, makeModel: makeModel, embed: embed,
    unknownWords: unknownWords, buildIndex: buildIndex, scoreAll: scoreAll,
    rank: rank, search: search, METHODS: METHODS
  };

  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.MuseumSearch = api;
})(typeof self !== "undefined" ? self : this);
