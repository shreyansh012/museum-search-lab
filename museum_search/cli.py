"""Command line: search, experiment, export-web."""

import argparse
import json
import sys

from . import data, search


def _print_results(results):
    if not results:
        print("No results. The query has no word that is in the vocabulary.")
        return
    for pos, (rec, score) in enumerate(results, 1):
        extra = ", ".join(x for x in (rec["type"], rec["culture"], rec["department"]) if x)
        print(f"{pos:2d}. {score:7.3f}  [{rec['id']}] {rec['title']}  ({extra})")


def cmd_search(args):
    records = data.load_records(args.data)
    model, doc_vecs = data.build(records)
    unknown = model.unknown_words(args.query)
    if unknown:
        print("Ignored words (not in vocabulary): " + ", ".join(unknown))
    if args.negative:
        unknown_neg = model.unknown_words(args.negative)
        if unknown_neg:
            print("Ignored negative words (not in vocabulary): " + ", ".join(unknown_neg))
    results = search.search(model, records, doc_vecs, args.query, args.negative,
                            args.weight, args.method, args.limit)
    _print_results(results)
    return 0


def cmd_experiment(args):
    from . import experiment
    text = experiment.run()
    print(text)
    if args.write:
        with open(args.write, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(f"\n(written to {args.write})")
    return 0


def cmd_export_web(args):
    records = data.load_records()
    model, _ = data.build(records)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(model.to_dict(), fh, separators=(",", ":"))
    print(f"wrote {args.out}: {len(model.terms)} words, {model.k} dimensions")
    return 0


def main(argv=None):
    # Some titles hold characters a Windows console cannot show. Never crash on them.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        prog="museum_search",
        description="Search museum records, with an optional 'less of this' query.")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="run one search")
    s.add_argument("query", help="what you want, e.g. gold")
    s.add_argument("--not", dest="negative", default="",
                   help="what you want less of, e.g. ring")
    s.add_argument("--weight", type=float, default=0.5,
                   help="how strongly to push away from --not (default 0.5)")
    s.add_argument("--method", choices=search.METHODS, default="score",
                   help="how to apply the negative (default score)")
    s.add_argument("--limit", type=int, default=10, help="how many results (default 10)")
    s.add_argument("--data", default=data.SAMPLE_PATH, help="path to the sample JSON file")
    s.set_defaults(func=cmd_search)

    e = sub.add_parser("experiment", help="compare the scoring methods")
    e.add_argument("--write", metavar="FILE", help="also save the report to FILE")
    e.set_defaults(func=cmd_experiment)

    w = sub.add_parser("export-web", help="write the model file the web page uses")
    w.add_argument("--out", default=data.MODEL_PATH)
    w.set_defaults(func=cmd_export_web)

    args = parser.parse_args(argv)
    if args.command == "search" and args.limit < 1:
        parser.error("--limit must be at least 1")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
