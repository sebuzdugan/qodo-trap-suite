#!/usr/bin/env python3
"""Planted-bug suite for testing pre-PR code review tools.

Each trap edits exactly ONE file. The resulting failure always surfaces in a
DIFFERENT file that the diff never opens. That gap is the whole point: a
reviewer reading only the diff cannot see it.

    python3 traps.py list
    python3 traps.py baseline
    python3 traps.py apply 1
    python3 traps.py diff 1
    python3 traps.py reset
    python3 traps.py verify 1
    python3 traps.py verify-all
"""

import argparse
import difflib
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRISTINE = os.path.join(ROOT, ".pristine")

TRAPS = {
    1: {
        "name": "Currency blast radius",
        "file": "app/money.py",
        "breaks_in": "app/reporting.py",
        "test": "tests/test_reporting.py",
        "skill": "qodo-codebase-wisdom",
        "why": "The changed file looks tidier. The break is in a reporting "
               "module the diff never opens.",
        "old": '''CURRENCY_EXPONENT = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
    "KRW": 0,
}


def to_minor_units(amount_major, currency):
    """Convert a major-unit amount to the currency's smallest unit.
    JPY and KRW have no minor unit, so their exponent is zero."""
    exponent = CURRENCY_EXPONENT[currency]
    return round(amount_major * (10 ** exponent))''',
        "new": '''def to_minor_units(amount_major, currency):
    # Simplified: every currency has two decimal places.
    return round(amount_major * 100)''',
    },
    2: {
        "name": "PII in the logs",
        "file": "app/notify.py",
        "breaks_in": "RULES.md rule 1",
        "test": "tests/test_notify_rules.py",
        "skill": "qodo-get-rules",
        "why": "Breaks a team rule, not a unit of logic. Only a reviewer that "
               "loaded the rules before writing catches this early.",
        "old": '''    log.info("password reset requested user_id=%s", user["id"])''',
        "new": '''    # Helpful for debugging bounced resets.
    log.info(
        "password reset requested user_id=%s email=%s",
        user["id"],
        user["email"],
    )''',
    },
    3: {
        "name": "Auth default",
        "file": "app/auth.py",
        "breaks_in": "app/api_invoices.py",
        "test": "tests/test_api_invoices.py",
        "skill": "qodo-review",
        "why": "Legacy accounts silently become admins. The admin endpoint "
               "itself never changed.",
        "old": '''    roles = user.get("roles")
    if not roles:
        return DEFAULT_ROLES
    return tuple(roles)''',
        "new": '''    roles = user.get("roles")
    if not roles:
        # Legacy accounts predate the roles table; grant the full set.
        return ("admin", "billing", "support")
    return tuple(roles)''',
    },
    4: {
        "name": "Daylight saving",
        "file": "app/schedule.py",
        "breaks_in": "app/billing_cycle.py",
        "test": "tests/test_billing_cycle.py",
        "skill": "qodo-review",
        "why": "'Tomorrow' becomes plus 24 hours. Billing fires an hour late "
               "on the DST day, in a file that was not touched.",
        "old": '''    naive_next = dt.replace(tzinfo=None) + timedelta(days=1)
    return naive_next.replace(tzinfo=dt.tzinfo)''',
        "new": '''    # Simpler: a day is 86400 seconds.
    return datetime.fromtimestamp(dt.timestamp() + 86400, tz=dt.tzinfo)''',
    },
    5: {
        "name": "Off-by-one paging",
        "file": "app/paging.py",
        "breaks_in": "app/export.py",
        "test": "tests/test_export.py",
        "skill": "qodo-review-resolver",
        "why": "The export silently drops one row per page. No error, no "
               "crash, just missing data.",
        "old": '''    start = (page - 1) * per_page
    return start, start + per_page''',
        "new": '''    start = (page - 1) * per_page
    return start, start + per_page - 1''',
    },
}

TRACKED = sorted({t["file"] for t in TRAPS.values()})


def _snapshot():
    """Keep an untouched copy of every file a trap can edit."""
    if os.path.isdir(PRISTINE):
        return
    for rel in TRACKED:
        dst = os.path.join(PRISTINE, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dst)


def reset():
    _snapshot()
    for rel in TRACKED:
        shutil.copy2(os.path.join(PRISTINE, rel), os.path.join(ROOT, rel))


def apply(n):
    _snapshot()
    trap = TRAPS[n]
    path = os.path.join(ROOT, trap["file"])
    src = open(path, encoding="utf-8").read()
    if trap["old"] not in src:
        raise SystemExit(
            "trap %d: anchor text not found in %s (run 'reset' first)"
            % (n, trap["file"])
        )
    open(path, "w", encoding="utf-8").write(src.replace(trap["old"], trap["new"], 1))


def show_diff(n):
    trap = TRAPS[n]
    old = trap["old"].splitlines(keepends=True)
    new = trap["new"].splitlines(keepends=True)
    added = sum(1 for line in new)
    removed = sum(1 for line in old)
    sys.stdout.writelines(
        difflib.unified_diff(
            old, new,
            fromfile="a/" + trap["file"],
            tofile="b/" + trap["file"],
        )
    )
    print("\n1 file changed, %d insertions(+), %d deletions(-)" % (added, removed))


def pytest_run():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "tests"],
        cwd=ROOT, capture_output=True, text=True,
    )
    tail = [l for l in proc.stdout.strip().splitlines() if l.strip()]
    summary = tail[-1] if tail else "(no output)"
    passed = _count(summary, "passed")
    failed = _count(summary, "failed")
    failing_tests = sorted({
        line.split()[1].split("::")[0]
        for line in proc.stdout.splitlines()
        if line.startswith("FAILED") and len(line.split()) > 1
    })
    return passed, failed, failing_tests, summary


def _count(summary, word):
    parts = summary.replace(",", " ").split()
    for i, p in enumerate(parts):
        if p == word and i:
            try:
                return int(parts[i - 1])
            except ValueError:
                return 0
    return 0


def cmd_list():
    print("%-3s %-24s %-18s %-24s %s" % ("#", "trap", "changes", "breaks in", "skill"))
    print("-" * 100)
    for n, t in sorted(TRAPS.items()):
        print("%-3d %-24s %-18s %-24s %s"
              % (n, t["name"], t["file"], t["breaks_in"], t["skill"]))


def cmd_baseline():
    reset()
    p, f, names, summary = pytest_run()
    print("baseline: %s" % summary)
    ok = f == 0 and p > 0
    print("baseline clean" if ok else "BASELINE NOT CLEAN")
    return 0 if ok else 1


def cmd_verify(n):
    reset()
    apply(n)
    p, f, names, summary = pytest_run()
    t = TRAPS[n]
    # The invariant that matters: the change is contained to one file, and
    # every resulting failure surfaces in the OTHER file, the one the diff
    # never opens. The number of tripped assertions is incidental.
    ok = f >= 1 and names == [t["test"]]
    print("trap %d  %-24s %s" % (n, t["name"], summary))
    print("   changed  : %s" % t["file"])
    print("   breaks in: %s" % t["breaks_in"])
    print("   failing  : %s" % (", ".join(names) or "(nothing)"))
    print("   contained: %s" % ("OK" if ok else "MISMATCH, expected only " + t["test"]))
    reset()
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=[
        "list", "baseline", "apply", "diff", "reset", "verify", "verify-all"])
    ap.add_argument("n", nargs="?", type=int)
    args = ap.parse_args()

    if args.command == "list":
        return cmd_list()
    if args.command == "baseline":
        return cmd_baseline()
    if args.command == "reset":
        reset()
        print("reset: all tracked files restored")
        return 0
    if args.command == "verify-all":
        rc = cmd_baseline()
        print()
        for n in sorted(TRAPS):
            rc |= cmd_verify(n)
            print()
        print("ALL TRAPS BEHAVE AS DOCUMENTED" if rc == 0 else "SOME TRAPS MISBEHAVED")
        return rc
    if args.n is None:
        raise SystemExit("%s needs a trap number 1-%d" % (args.command, len(TRAPS)))
    if args.command == "apply":
        apply(args.n)
        t = TRAPS[args.n]
        print("applied trap %d (%s) to %s" % (args.n, t["name"], t["file"]))
        print("expect the break in: %s" % t["breaks_in"])
        return 0
    if args.command == "diff":
        return show_diff(args.n)
    if args.command == "verify":
        return cmd_verify(args.n)


if __name__ == "__main__":
    sys.exit(main() or 0)
