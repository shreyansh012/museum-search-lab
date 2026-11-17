# Data

## Source

Object records from The Metropolitan Museum of Art Open Access API.

- Documentation: https://metmuseum.github.io/
- Search endpoint used: `https://collectionapi.metmuseum.org/public/collection/v1.1/search?q=<word>&hasImages=true&isPublicDomain=true&limit=26&offset=0`
- Object endpoint used: `https://collectionapi.metmuseum.org/public/collection/v1/objects/<objectID>`

The older `v1/search` endpoint was scheduled for retirement on 2026-10-01 per the documentation, so this repo uses `v1.1/search`. The object endpoint is unchanged.

## Licence

The museum states on the documentation page that it has waived copyright and related rights to the dataset under Creative Commons Zero (CC0). Licence text: https://creativecommons.org/publicdomain/zero/1.0/

Credit is not required under CC0. Suggested credit used in this repo:

> Data: The Metropolitan Museum of Art, New York. Open Access, Creative Commons Zero (CC0). https://www.metmuseum.org/

The museum also notes that some records describe works that are still under copyright. This repo keeps only records where the API field `isPublicDomain` is `true`.

## What is in `data/sample.json`

- Fetched on 2026-11-17 with `python -m museum_search.fetch_data`.
- 315 records, sorted by object ID (range 229 to 774458).
- 108 of the 315 records have at least one tag. The rest have an empty tag list.
- Each record keeps these fields, copied from the API with extra spaces removed: `id` (from `objectID`), `title`, `type` (from `objectName`), `culture`, `medium`, `tags` (the `term` of each tag), `department`, and `url` (from `objectURL`, a link to the museum's page for that object).
- No other field is stored. Images are not stored or loaded.

## How the sample was chosen

The fetch script runs 18 search words (vase, sword, painting, textile, chair, necklace, bowl, print, sculpture, helmet, ring, tapestry, clock, coin, mask, armor, dress, fan). For each word it takes up to the first 26 matching object IDs from the search result. It then downloads each object, keeps it if `isPublicDomain` is true and the title is not empty, and stops at 400 records. Here 315 were kept.

This is a convenience sample, not a random or balanced sample. Some object types (bowls, coins, helmets, vases, armor) are over-represented because they were search words. A new run may return a different set, because the museum updates its records and search ranking.

## Synthetic data

None. All records are real museum records.

## Changing the data

Any file with the same fields works: `python -m museum_search search silk --data path/to/file.json`. After replacing `data/sample.json`, run `python -m museum_search export-web` so the web page matches, and run the tests.
