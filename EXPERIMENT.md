# Experiment report

Records: 315. Vocabulary: 235 words. Dimensions: 32. Window: first 10 results.

Methods: `score` = cos(d,q) - w*cos(d,n). `vector` = cos(d, q' - w*n') with q' and n' scaled to length 1. `vector-raw` = cos(d, q - w*n) with the vectors as the model gives them.

## 1. `score` versus `vector`

For each pair and weight: is the order the same, and how big is the largest gap between `vector` x |q' - w*n'| and `score`?

| query | not | w | same order | max gap | score range | vector range |
|---|---|---|---|---|---|---|
| gold | ring | 0.25 | yes | 1.1e-16 | -0.15 to 0.50 | -0.15 to 0.51 |
| gold | ring | 0.5 | yes | 1.7e-16 | -0.36 to 0.50 | -0.36 to 0.50 |
| gold | ring | 1.0 | yes | 1.7e-16 | -0.79 to 0.50 | -0.65 to 0.41 |
| gold | ring | 2.0 | yes | 4.4e-16 | -1.65 to 0.53 | -0.82 to 0.26 |
| silk | dress | 0.25 | yes | 1.1e-16 | -0.25 to 0.65 | -0.27 to 0.72 |
| silk | dress | 0.5 | yes | 1.9e-16 | -0.29 to 0.66 | -0.33 to 0.74 |
| silk | dress | 1.0 | yes | 2.2e-16 | -0.59 to 0.68 | -0.57 to 0.65 |
| silk | dress | 2.0 | yes | 4.4e-16 | -1.49 to 0.72 | -0.84 to 0.40 |
| glass | vase | 0.25 | yes | 1.1e-16 | -0.24 to 0.83 | -0.25 to 0.84 |
| glass | vase | 0.5 | yes | 1.7e-16 | -0.42 to 0.81 | -0.40 to 0.77 |
| glass | vase | 1.0 | yes | 2.2e-16 | -0.78 to 0.75 | -0.60 to 0.58 |
| glass | vase | 2.0 | yes | 4.4e-16 | -1.56 to 0.68 | -0.74 to 0.32 |
| wood | chair | 0.25 | yes | 1.7e-16 | -0.27 to 0.57 | -0.29 to 0.61 |
| wood | chair | 0.5 | yes | 1.4e-16 | -0.47 to 0.52 | -0.50 to 0.56 |
| wood | chair | 1.0 | yes | 1.5e-16 | -0.87 to 0.45 | -0.78 to 0.40 |
| wood | chair | 2.0 | yes | 2.2e-16 | -1.69 to 0.29 | -0.90 to 0.15 |
| bronze | sculpture | 0.25 | yes | 1.1e-16 | -0.37 to 0.79 | -0.36 to 0.76 |
| bronze | sculpture | 0.5 | yes | 1.1e-16 | -0.59 to 0.80 | -0.53 to 0.71 |
| bronze | sculpture | 1.0 | yes | 2.2e-16 | -1.04 to 0.82 | -0.73 to 0.58 |
| bronze | sculpture | 2.0 | yes | 4.4e-16 | -1.93 to 0.87 | -0.86 to 0.39 |
| iran | bowl | 0.25 | yes | 2.2e-16 | -0.33 to 0.90 | -0.33 to 0.89 |
| iran | bowl | 0.5 | yes | 3.3e-16 | -0.53 to 0.88 | -0.50 to 0.82 |
| iran | bowl | 1.0 | yes | 2.2e-16 | -0.94 to 0.84 | -0.70 to 0.63 |
| iran | bowl | 2.0 | yes | 4.4e-16 | -1.84 to 0.77 | -0.86 to 0.36 |
| italian | armor | 0.25 | yes | 1.1e-16 | -0.38 to 0.55 | -0.40 to 0.58 |
| italian | armor | 0.5 | yes | 1.1e-16 | -0.51 to 0.42 | -0.52 to 0.43 |
| italian | armor | 1.0 | yes | 2.2e-16 | -0.89 to 0.41 | -0.74 to 0.35 |
| italian | armor | 2.0 | yes | 2.2e-16 | -1.76 to 0.39 | -0.90 to 0.20 |
| ceramic | bowl | 0.25 | yes | 1.1e-16 | -0.24 to 0.75 | -0.25 to 0.77 |
| ceramic | bowl | 0.5 | yes | 1.1e-16 | -0.44 to 0.73 | -0.43 to 0.72 |
| ceramic | bowl | 1.0 | yes | 2.2e-16 | -0.85 to 0.69 | -0.67 to 0.55 |
| ceramic | bowl | 2.0 | yes | 2.2e-16 | -1.72 to 0.62 | -0.84 to 0.30 |

All orders the same: yes. Largest gap anywhere: 4.4e-16.

Reading: the order is the same because cos(d, q' - w*n') equals (cos(d,q') - w*cos(d,n')) divided by one number that does not depend on d. The two methods differ only in the size of the scores, not in the ranking. At w = 2 the scores go below zero in both. That is expected, not a bug.

## 2. `vector-raw` versus `score`

Overlap is how many of the first 10 results the two methods share (10 means the same set). 'Literal' is how many of the first 10 records contain the negative word in their text.

| query | not | w | overlap | literal: plain | literal: score | literal: raw |
|---|---|---|---|---|---|---|
| gold | ring | 0.25 | 10 | 7 | 0 | 0 |
| gold | ring | 0.5 | 10 | 7 | 0 | 0 |
| gold | ring | 1.0 | 9 | 7 | 0 | 0 |
| gold | ring | 2.0 | 9 | 7 | 0 | 0 |
| silk | dress | 0.25 | 5 | 9 | 6 | 1 |
| silk | dress | 0.5 | 9 | 9 | 0 | 0 |
| silk | dress | 1.0 | 10 | 9 | 0 | 0 |
| silk | dress | 2.0 | 8 | 9 | 0 | 0 |
| glass | vase | 0.25 | 9 | 5 | 5 | 4 |
| glass | vase | 0.5 | 7 | 5 | 3 | 0 |
| glass | vase | 1.0 | 9 | 5 | 0 | 0 |
| glass | vase | 2.0 | 10 | 5 | 0 | 0 |
| wood | chair | 0.25 | 9 | 6 | 5 | 4 |
| wood | chair | 0.5 | 9 | 6 | 2 | 1 |
| wood | chair | 1.0 | 10 | 6 | 0 | 0 |
| wood | chair | 2.0 | 8 | 6 | 0 | 0 |
| bronze | sculpture | 0.25 | 9 | 5 | 5 | 4 |
| bronze | sculpture | 0.5 | 10 | 5 | 3 | 3 |
| bronze | sculpture | 1.0 | 9 | 5 | 1 | 0 |
| bronze | sculpture | 2.0 | 10 | 5 | 0 | 0 |
| iran | bowl | 0.25 | 8 | 3 | 1 | 1 |
| iran | bowl | 0.5 | 7 | 3 | 1 | 0 |
| iran | bowl | 1.0 | 6 | 3 | 1 | 0 |
| iran | bowl | 2.0 | 6 | 3 | 0 | 0 |
| italian | armor | 0.25 | 8 | 9 | 6 | 4 |
| italian | armor | 0.5 | 6 | 9 | 4 | 0 |
| italian | armor | 1.0 | 9 | 9 | 0 | 0 |
| italian | armor | 2.0 | 9 | 9 | 0 | 0 |
| ceramic | bowl | 0.25 | 9 | 2 | 2 | 1 |
| ceramic | bowl | 0.5 | 9 | 2 | 1 | 0 |
| ceramic | bowl | 1.0 | 10 | 2 | 0 | 0 |
| ceramic | bowl | 2.0 | 8 | 2 | 0 | 0 |

`vector-raw` shares all 10 results with `score` in 8 of 32 runs. It differs in 24 runs. Lowest overlap: 5 of 10.

Reading: after the squeeze to a few dimensions, the query and negative vectors have different lengths. With raw vectors, cos(d, q - w*n) is the same as `score` with a changed weight w' = w * |n| / |q|. So the weight w does not mean the same thing for each pair. The next table checks this: does `vector-raw` at w give the same order as `score` at w'?

| query | not | length ratio n/q | w | same order as score at w' |
|---|---|---|---|---|
| gold | ring | 1.29 | 0.25 | yes |
| gold | ring | 1.29 | 0.5 | yes |
| gold | ring | 1.29 | 1.0 | yes |
| gold | ring | 1.29 | 2.0 | yes |
| silk | dress | 1.46 | 0.25 | yes |
| silk | dress | 1.46 | 0.5 | yes |
| silk | dress | 1.46 | 1.0 | yes |
| silk | dress | 1.46 | 2.0 | yes |
| glass | vase | 1.66 | 0.25 | yes |
| glass | vase | 1.66 | 0.5 | yes |
| glass | vase | 1.66 | 1.0 | yes |
| glass | vase | 1.66 | 2.0 | yes |
| wood | chair | 1.19 | 0.25 | yes |
| wood | chair | 1.19 | 0.5 | yes |
| wood | chair | 1.19 | 1.0 | yes |
| wood | chair | 1.19 | 2.0 | yes |
| bronze | sculpture | 1.22 | 0.25 | yes |
| bronze | sculpture | 1.22 | 0.5 | yes |
| bronze | sculpture | 1.22 | 1.0 | yes |
| bronze | sculpture | 1.22 | 2.0 | yes |
| iran | bowl | 3.57 | 0.25 | yes |
| iran | bowl | 3.57 | 0.5 | yes |
| iran | bowl | 3.57 | 1.0 | yes |
| iran | bowl | 3.57 | 2.0 | yes |
| italian | armor | 1.87 | 0.25 | yes |
| italian | armor | 1.87 | 0.5 | yes |
| italian | armor | 1.87 | 1.0 | yes |
| italian | armor | 1.87 | 2.0 | yes |
| ceramic | bowl | 2.56 | 0.25 | yes |
| ceramic | bowl | 2.56 | 0.5 | yes |
| ceramic | bowl | 2.56 | 1.0 | yes |
| ceramic | bowl | 2.56 | 2.0 | yes |

All the same: yes. So `vector-raw` is not a different ranking idea. It is `score` with a weight that moves with the length of the two vectors.

## 3. One example: `silk`, less of `dress`, w = 0.5

plain (no negative):

1. 0.708  Dress (Dress, Costume Institute)
2. 0.675  Dress (Dress, Costume Institute)
3. 0.645  Textile (Textile, Medieval Art)
4. 0.638  Dress (Dress, Costume Institute)
5. 0.638  Dress (Dress, Costume Institute)

score:

1. 0.662  Textile (Textile, Medieval Art)
2. 0.534  Painting (Painting, Asian Art)
3. 0.510  Textile (Textile fragment, Islamic Art)
4. 0.393  Mask (Mask, Arms and Armor)
5. 0.370  Helmet (Helmet, Costume Institute)

vector-raw:

1. 0.720  Textile (Textile, Medieval Art)
2. 0.560  Painting (Painting, Asian Art)
3. 0.551  Textile (Textile fragment, Islamic Art)
4. 0.417  Mask (Mask, Arms and Armor)
5. 0.379  Armor (Armor, Arms and Armor)

## 4. Edge cases checked

- An empty, blank or unknown-word negative gives exactly the plain scores, for all three methods.
- Negative equal to the query with w = 1 gives a zero vector. All scores are 0.0: True.
- A query with no known word returns 0 results.

## Limits of this experiment

- 315 records and 8 hand-picked pairs. This shows behaviour, not a general result.
- No human judged the results. 'Literal' counts only check one thing: whether the negative word still appears.
- With so few records, many of the first results are near-copies (same object type from the same department).
