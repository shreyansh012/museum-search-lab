# museum-search-lab

"Less of this" search over public museum records.

## What this demo shows

It builds its own word vectors from 315 public-domain object records (title, type, culture, medium, tags, department) using TF-IDF and a truncated SVD, written with the Python standard library only. You type what you want and, optionally, what you want less of, and the search pushes records that match the second phrase down the list. A small experiment compares two ways to apply the "less of this" term, and a static web page runs the same search in the browser with plain JavaScript.

Subtracting vectors in an embedding space is a known technique, and prior art exists. Examples are the "king - man + woman" word-vector analogies, negative feedback in Rocchio-style relevance feedback, and TF-IDF with SVD, which is classic latent semantic analysis. This repo makes no claim of novelty. It is a small, readable, tested version for learning and demonstration.

AI-assisted, with tests and review gates.

## How to run it

You need Python 3.11 or newer. No packages to install, no network, no account, no key. On Linux or macOS, type `python3` where these commands say `python`.

Run the tests:

```
python -m unittest discover -s tests -v
```

Search from the command line. `--not` is the "less of this" phrase:

```
python -m museum_search search silk
python -m museum_search search silk --not dress --weight 0.5 --limit 5
python -m museum_search search silk --not dress --method vector
```

Methods: `score` (default), `vector`, `vector-raw`. They are explained below.

Run the experiment and save the report:

```
python -m museum_search experiment --write EXPERIMENT.md
```

Open the web page. Browsers block file loading from a plain file, so start a small local server in the repo folder, then open the address:

```
python -m http.server 8000
```

Open `http://localhost:8000/web/` in a browser. If you change the data or the model rules, rebuild the model file the page uses:

```
python -m museum_search export-web
```

To fetch a fresh sample (needs network, and may return different records than the ones in the repo):

```
python -m museum_search.fetch_data
```

## How the search works

1. Each record becomes one text: title, type, culture, medium, tags and department.
2. Words are lower-cased, accents are dropped, simple plurals are cut, and very common words are removed.
3. Each text becomes a TF-IDF row. Rare words weigh more.
4. A truncated SVD (block power iteration, 32 dimensions, fixed random seed) squeezes the 235-word space into 32 numbers per text.
5. Your query and your "less of this" phrase go through the same steps.

Three ways to score a record `d`, with query vector `q`, negative vector `n` and weight `w`:

| method | formula |
|---|---|
| `score` | cos(d, q) - w * cos(d, n) |
| `vector` | cos(d, q' - w * n'), where q' and n' are q and n scaled to length 1 |
| `vector-raw` | cos(d, q - w * n), using the vectors as the model gives them |

## What the experiment found

Full tables are in `EXPERIMENT.md`. These numbers come from the run in this repo: 315 records, 8 query pairs, 4 weights (32 runs).

- `score` and `vector` gave the same order in all 32 runs. This is not luck. When q' and n' have length 1, cos(d, q' - w*n') equals cos(d, q') - w*cos(d, n') divided by one number that is the same for every record. So the two methods differ in the size of the scores, not in the ranking. At w = 2 the scores go below zero in both.
- `vector-raw` gave a different set of first 10 results in 24 of the 32 runs (lowest overlap with `score`: 5 of 10). The reason is that it equals `score` with a changed weight, w * |n| / |q|. Different word pairs give different length ratios, so the same w pushes harder for some pairs than for others. The experiment checks this equivalence in all 32 runs.
- The negative phrase does push records out of the way. For "silk, less of dress" at w = 0.5, 9 of the first 10 plain results contain the word "dress". With the negative, none do. The records that replace them are less on-topic, which is the price of the push.
- An empty, blank or unknown-word negative gives exactly the plain scores. A negative equal to the query at w = 1 gives all-zero scores, not an error.

## What it does NOT prove

- It does not show that this search is better than plain keyword search. No person judged the results.
- 315 records and 8 hand-picked pairs is a small test. The findings above describe this data, not museum data in general.
- The vocabulary has only 235 words, because words that occur in a single record are dropped. A word that is not in it is ignored. The CLI and the web page say when that happens.
- The SVD is a plain method run for a fixed number of steps. It is not checked against a reference library, and it is slow for large data.
- The records are the museum's own metadata. Sparse or uneven metadata (only 108 of the 315 records have tags) limits what any text search can find.
- The determinism test compares two builds in one run. It cannot catch tiny differences in math libraries between machines. Exported numbers are rounded to 6 decimals, and the browser-versus-Python test allows for tiny differences.
- The records come from one museum and one point in time. See `DATA.md`.

## Files

- `museum_search/` : the code (vectors, search, command line, experiment, fetch script).
- `web/` : the static page (`index.html`, `search.js`) and the model file it loads (`model.json`).
- `data/sample.json` : the record sample. `DATA.md` says where it came from.
- `tests/` : unit tests (standard library `unittest`). One test compares the browser code with the Python code, and is skipped if the `node` command is not installed.
- `DECISIONS.md` : why things are built this way, and what was rejected.
- `EXPERIMENT.md` : the generated experiment report.

## Licence

Code: MIT, see `LICENSE`. Data: CC0 from the museum, see `DATA.md`.
