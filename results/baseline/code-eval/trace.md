### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by exploring the workspace structure.



### Tool call: ls
{"path": "workspace"}

### Tool call: glob
{"pattern": "workspace/**/*.py"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Assistant




### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md"}

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Assistant




### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool call: execute
{"command": "cd workspace && wc -c bookings/timeutil.py && python -m pytest tests -q 2>&1 | tail -30"}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
513 bookings/timeutil.py

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
________________________ test_billable_blocks_rounds_up ________________________

    def test_billable_blocks_rounds_up():
>       assert billable_blocks(20) == 2
E       assert 1 == 2
E        +  where 1 = billable_blocks(20)

tests/test_bookings.py:10: AssertionError
=========================== short test summary info ============================
FAILED tests/test_bookings.py::test_total_minutes_mixed_formats - ValueError:...
FAILED tests/test_bookings.py::test_billable_blocks_rounds_up - assert 1 == 2
2 failed, 1 passed in 0.04s

[Command succeeded with exit code 0]

### Assistant




### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 25}

### Tool call: execute
{"command": "cd workspace && python -c \"\nprint(open('bookings/timeutil.py').read())\n\""}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))


[Command succeeded with exit code 0]

### Assistant




### Tool call: ls
{"path": "/"}

### Tool call: glob
{"pattern": "**/*.md"}

### Tool call: glob
{"pattern": "**/*.{toml,cfg,ini,txt,yaml,yml}"}

### Tool result
['/workspace/']

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md']

### Tool result
No files found

### Assistant
Now I understand the bugs. Let me check for any conventions/config files and then fix the source.



### Tool call: execute
{"command": "cd workspace && ls -la && ls -la bookings tests"}

### Tool result
total 28
drwxrwxrwx 5 tavan tavan 4096 Oct  6 18:49 .
drwx------ 3 tavan tavan 4096 Oct  6 18:49 ..
drwxr-xr-x 3 tavan tavan 4096 Oct  6 18:49 .pytest_cache
-rwxrwxrwx 1 tavan tavan   54 Oct  6 18:37 CHANGELOG.md
-rwxrwxrwx 1 tavan tavan  118 Oct  6 18:37 README.md
drwxrwxrwx 3 tavan tavan 4096 Oct  6 18:37 bookings
drwxrwxrwx 3 tavan tavan 4096 Oct  6 18:37 tests
bookings:
total 32
drwxrwxrwx 3 tavan tavan 4096 Oct  6 18:37 .
drwxrwxrwx 5 tavan tavan 4096 Oct  6 18:49 ..
-rwxrwxrwx 1 tavan tavan   22 Oct  6 18:37 __init__.py
drwxrwxrwx 2 tavan tavan 4096 Oct  6 09:34 __pycache__
-rwxrwxrwx 1 tavan tavan  333 Oct  6 18:37 billing.py
-rwxrwxrwx 1 tavan tavan  211 Oct  6 18:37 calendar_export.py
-rwxrwxrwx 1 tavan tavan  467 Oct  6 18:37 schedule.py
-rwxrwxrwx 1 tavan tavan  513 Oct  6 18:37 timeutil.py

tests:
total 16
drwxrwxrwx 3 tavan tavan 4096 Oct  6 18:37 .
drwxrwxrwx 5 tavan tavan 4096 Oct  6 18:49 ..
drwxrwxrwx 2 tavan tavan 4096 Oct  6 09:34 __pycache__
-rwxrwxrwx 1 tavan tavan  371 Oct  6 18:37 test_bookings.py

[Command succeeded with exit code 0]

### Assistant
No config files present. Now let me fix the three bugs.



### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n_HM_RE = re.compile(r\"(\\d+)h(\\d+)m\")\n_H_RE = re.compile(r\"(\\d+)h\")\n_M_RE = re.compile(r\"(\\d+)m\")\n_CLOCK_RE = re.compile(r\"(\\d+):(\\d{2})\")\n_BARE_RE = re.compile(r\"(\\d+)\")\n\n\ndef parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    stripped = text.strip()\n\n    m = _HM_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n\n    m = _H_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1)) * 60\n\n    m = _M_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1))\n\n    m = _CLOCK_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n\n    m = _BARE_RE.fullmatch(stripped)\n    if m:\n        return int(m.group(1))\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes, block=15):\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(f\"minutes must be >= 0, got {minutes!r}\")\n    return math.ceil(minutes / block)\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations):\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    return [*slots, slot]\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool result
Updated file /workspace/bookings/billing.py

### Tool result
Updated file /workspace/bookings/schedule.py

### Assistant




### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5 && python -c \"\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.calendar_export import slot_end\nassert parse_duration('1h30m')==90\nassert parse_duration('2h')==120\nassert parse_duration('45m')==45\nassert parse_duration('1:30')==90\nassert parse_duration('45')==45\nassert parse_duration('  2h  ')==120\nassert parse_duration('0h0m')==0\nfor bad in ['', 'abc', '1h30', 'h', '1.5h', '-5m']:\n    try:\n        parse_duration(bad); print('NO RAISE', bad)\n    except ValueError: pass\nassert billable_blocks(0)==0\nassert billable_blocks(15)==1\nassert billable_blocks(16)==2\nassert billable_blocks(20)==2\nassert billable_blocks(45)==3\nassert billable_blocks(30, block=30)==1\ntry:\n    billable_blocks(-1); print('NO RAISE neg')\nexcept ValueError: pass\nassert add_slot('a')==['a']\nassert add_slot('b')==['b']\nassert add_slot('c', ['a','b'])==['a','b','c']\nassert add_slot('c', ['a','b'])==['a','b','c']\nassert total_minutes([])==0\nassert total_minutes(['1h30m','2h'])==210\nassert slot_end(60,'1h30m')==150\nprint('all spec checks OK')\n\""}

### Tool result
...                                                                      [100%]
3 passed in 0.01s
all spec checks OK

[Command succeeded with exit code 0]

### Assistant
All tests pass and the docstring-specified behaviors are verified. Let me do a final full run.



### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -3"}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
All 3 tests pass and the docstring-specified behavior is verified.

## Summary

I fixed three bugs in the `bookings` package source (no test files were touched):

**`bookings/timeutil.py` — `parse_duration`**
The regex only matched the `"1h30m"` form, so `"2h"`, `"45m"`, `"1:30"`, and bare `"45"` all raised `ValueError`. I rewrote it to handle every documented format (hours+minutes, hours only, minutes only, `H:MM` clock form, and bare minutes), still stripping surrounding whitespace and raising `ValueError` for anything unrecognized. I hoisted the patterns to module-level compiled constants to avoid recompiling on each call.

**`bookings/billing.py` — `billable_blocks`**
It used `round()`, which rounds to nearest (and to even on ties), so 20 minutes gave 1 block instead of 2. The docstring requires always rounding **up**, so I switched to `math.ceil`. I also added the documented `ValueError` for negative `minutes`, which was previously unenforced.

**`bookings/schedule.py` — `add_slot`**
It used a mutable default argument (`slots=[]`) and mutated it in place, so state leaked across calls. I changed the default to `None` and now return a brand-new list (`[*slots, slot]`), satisfying the "separate calls must not share state" requirement.

`calendar_export.slot_end` was already correct (it delegates to the fixed `parse_duration`).