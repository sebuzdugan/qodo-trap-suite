# qodo-trap-suite

Five planted bugs for testing **pre-PR** code review tools.

The rule every trap follows:

> The change touches exactly **one** file. The break surfaces in a **different**
> file that the diff never opens.

That gap is the whole test. A reviewer reading only the diff sees a tidier
function. A reviewer that understands the codebase names the file that broke.

## The traps

| # | Trap | Changes | Breaks in | Toolbox skill |
|---|------|---------|-----------|---------------|
| 1 | Currency blast radius | `app/money.py` | `app/reporting.py` | qodo-codebase-wisdom |
| 2 | PII in the logs | `app/notify.py` | `RULES.md` rule 1 | qodo-get-rules |
| 3 | Auth default | `app/auth.py` | `app/api_invoices.py` | qodo-review |
| 4 | Daylight saving | `app/schedule.py` | `app/billing_cycle.py` | qodo-review |
| 5 | Off-by-one paging | `app/paging.py` | `app/export.py` | qodo-review-resolver |

Trap 2 is the odd one out on purpose: it breaks a **team rule**, not a unit of
logic. Only a reviewer that loaded the rules *before* the code was written
catches it early.

## Setup

```bash
python3 -m venv .venv && ./.venv/bin/pip install pytest
```

## Use

```bash
./.venv/bin/python traps.py list          # what each trap does
./.venv/bin/python traps.py baseline      # prove the suite is green
./.venv/bin/python traps.py diff 1        # the diff a reviewer would see
./.venv/bin/python traps.py apply 1       # plant trap 1, then run your reviewer
./.venv/bin/python traps.py reset         # restore every file
./.venv/bin/python traps.py verify-all    # self-check all five
```

`apply` leaves the bug in the working tree **uncommitted**, which is the state
every pre-PR reviewer is meant to read:

```bash
./.venv/bin/python traps.py apply 1
coderabbit review --uncommitted
cubic review
# or, inside Claude Code / Codex with the Qodo skills installed:
#   "review my changes before I open the PR"
#   "which files break if I change the currency helper?"
./.venv/bin/python traps.py reset
```

## Verified behaviour

`traps.py verify-all`, run on this suite:

```
baseline: 11 passed
trap 1  Currency blast radius   2 failed, 9 passed   -> only tests/test_reporting.py
trap 2  PII in the logs         1 failed, 10 passed  -> only tests/test_notify_rules.py
trap 3  Auth default            1 failed, 10 passed  -> only tests/test_api_invoices.py
trap 4  Daylight saving         1 failed, 10 passed  -> only tests/test_billing_cycle.py
trap 5  Off-by-one paging       2 failed, 9 passed   -> only tests/test_export.py
ALL TRAPS BEHAVE AS DOCUMENTED
```

Trap 1 in isolation reproduces the figures used in the article: `app/money.py`
changes by **+3 −14**, and `tests/test_reporting.py` goes from **3 passed** to
**2 failed, 1 passed**, with both failures in the reporting module.

## Scoring a tool

```bash
cp scorecard/results.template.json scorecard/results.json
# fill in caught / named_downstream per tool per trap
./.venv/bin/python scorecard/make_scorecard.py scorecard/results.json
```

Unfilled rows print as `OPEN`. Nothing is ever reported as a pass by default.

The question to score is not "did it complain". It is:

> Did it name the file that broke, the one that never appeared in the diff?
