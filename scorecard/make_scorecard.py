#!/usr/bin/env python3
"""Turn results.json into the scorecard table for the follow-up post.

    python3 scorecard/make_scorecard.py scorecard/results.json

Unfilled runs (caught == null) print as OPEN so nothing is ever silently
reported as a pass.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from traps import TRAPS  # noqa: E402


def mark(run):
    if run.get("caught") is None:
        return "OPEN"
    if not run["caught"]:
        return "miss"
    return "caught + named" if run.get("named_downstream") else "caught"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "scorecard/results.json"
    data = json.load(open(path, encoding="utf-8"))
    tools = data["tools"]
    by = {(r["trap"], r["tool"]): r for r in data["runs"]}

    w = 26
    print("| %-*s | %s |" % (w, "trap", " | ".join("%-14s" % t for t in tools)))
    print("|%s|%s|" % ("-" * (w + 2), "|".join("-" * 16 for _ in tools)))
    for n, t in sorted(TRAPS.items()):
        label = "%d. %s" % (n, t["name"])
        cells = [mark(by.get((n, tool), {})) for tool in tools]
        print("| %-*s | %s |" % (w, label, " | ".join("%-14s" % c for c in cells)))

    open_runs = sum(1 for r in data["runs"] if r.get("caught") is None)
    print("\n%d of %d runs still OPEN." % (open_runs, len(data["runs"])))
    if open_runs:
        print("Do not publish a scorecard with OPEN rows as if it were complete.")


if __name__ == "__main__":
    main()
