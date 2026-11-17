"""Download a small sample of object records from the Met Open Access API.

Usage:  python -m museum_search.fetch_data

Writes data/sample.json.
Only records marked as public domain are kept.
Needs network access. The sample file is already in the repo,
so you only run this if you want to refresh it.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
BASE_V11 = "https://collectionapi.metmuseum.org/public/collection/v1.1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Several different search words, so the sample has a mix of object kinds.
QUERIES = [
    "vase", "sword", "painting", "textile", "chair", "necklace",
    "bowl", "print", "sculpture", "helmet", "ring", "tapestry",
    "clock", "coin", "mask", "armor", "dress", "fan",
]
PER_QUERY = 26
TARGET = 400


def get_json(url, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": "demo-fetch/1.0"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # network errors, bad JSON, 403/404
            if attempt == tries - 1:
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def clean(text):
    return " ".join((text or "").split())


def to_record(obj):
    tags = [clean(t.get("term", "")) for t in (obj.get("tags") or [])]
    return {
        "id": obj.get("objectID"),
        "title": clean(obj.get("title")),
        "type": clean(obj.get("objectName")),
        "culture": clean(obj.get("culture")),
        "medium": clean(obj.get("medium")),
        "tags": [t for t in tags if t],
        "department": clean(obj.get("department")),
        "url": obj.get("objectURL", ""),
    }


def main():
    ids = []
    seen = set()
    for q in QUERIES:
        # v1.1 search is paged with offset and limit (the old v1 search was scheduled for retirement on 2026-10-01).
        qs = urllib.parse.urlencode(
            {"q": q, "hasImages": "true", "isPublicDomain": "true",
             "limit": PER_QUERY, "offset": 0})
        data = get_json(f"{BASE_V11}/search?{qs}")
        if not data or not data.get("objectIDs"):
            print(f"search failed or empty: {q}", file=sys.stderr)
            continue
        for oid in data["objectIDs"]:
            if oid not in seen:
                seen.add(oid)
                ids.append(oid)

    records = []
    for oid in ids:
        obj = get_json(f"{BASE}/objects/{oid}")
        time.sleep(0.05)
        if not obj or not obj.get("isPublicDomain"):
            continue
        rec = to_record(obj)
        if not rec["title"]:
            continue
        records.append(rec)
        if len(records) >= TARGET:
            break

    if len(records) < 100:
        print(f"only {len(records)} records fetched; not writing", file=sys.stderr)
        sys.exit(1)

    records.sort(key=lambda r: r["id"])
    path = os.path.join(ROOT, "data", "sample.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=0)
    print(f"wrote {len(records)} records")


if __name__ == "__main__":
    main()
