# How to run Discovery

You need Python 3. Nothing to install. (`hybrid/net_as_lens.py` needs
numpy and `extend/functions.py` a word list; nothing else does.)

## Run it on a file

```
python discovery.py FILE
```

Two files get written next to the input: `FILE.record.txt` (readable
by people) and `FILE.record.json` (readable by programs). The text
record also gets printed to the screen. When you use `--frame` or
`--separators`, the file names include that so different runs of the
same file don't overwrite each other (like `FILE.frame8.record.txt` or
`FILE.sep2.record.txt`). With `--memory` the name includes `.mN`,
where N is how many signals the memory has seen after this one.

## Options

| option | what it does | default |
|---|---|---|
| `--lens raw\|ascii\|utf8\|octal` | how words are displayed in the record (changes the look, not the results) | `raw` (hex) |
| `--limit BYTES` | only read the first BYTES of the file | the whole file |
| `--widest BITS` | widest word size to test | 64 |
| `--frame BITS` | skip the word-size detection and use this width | auto-detected |
| `--separators N` | use the N most common words as separators instead of just one | 1 |
| `--separators HEX,HEX` | pick the separator words yourself, in hex (`20,0a` means space and newline; one word is `0x20` or `20,`, since digits alone are a count) | |
| `--cap PARTS` | stop the mint loop if the pool gets bigger than this | 1000000 |
| `--memory FILE` | load a saved pool from FILE, compare this signal against it, then save the updated pool back (JSON; one memory holds signals read at one frame) | none |
| `--top N` | how many rows to show per table in the text record | 25 |
| `--out DIR` | where to write the record files | next to the input |
| `--quiet` | don't print the record to the screen | |

The JSON record always has everything. `--top` only affects the
text printout. The frame is decided from the first 64 KB of the file.
An option the program doesn't have, or one with its value left off, is
refused with a message rather than ignored.

## The examples

```
python discovery.py examples/text/alice.txt --lens ascii
python discovery.py examples/text/alice.txt --lens ascii --separators 20,0a
python discovery.py examples/german/ep-00-01-17.de --lens utf8
python discovery.py examples/code/input/hello --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code --frame 8
python discovery.py examples/code/input/discovery.py --lens ascii --out examples/code
python discovery.py examples/agc/input/luminary099.rope --lens octal --out examples/agc
python discovery.py examples/agc/input/luminary099.agc --lens ascii --out examples/agc --separators 2

cd examples/memory
python ../../discovery.py alice-first-half.txt  --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py ep-00-01-17.de        --lens utf8  --memory alice.memory
```

Each one stands on its own, and its folder's BREAKDOWN.md says what to
look for in the record it writes. `run_examples.sh` is the optional
bulk run: all of these plus the extensions and the hybrid scripts,
rebuilding every record in the repo.

## Use it from Python

```python
import discovery
R = discovery.Root('some/file', lens='ascii')   # the signal as read: R.words, R.frame, R.L0, R.pool, R.part_of
R.all_levels()                                  # every level, as discover() runs them: R.levels
txt, js = discovery.discover('some/file', lens='ascii', quiet=True)   # Root plus the record written
```

`Root` is the root of every program built on Discovery (the scripts in
`extend/` are `Root` plus one new thing) and of `discover()` itself.
Or call the steps one at a time — each is a plain function:

```python
data, bits = discovery.read_signal('some/file')
frame, profile, score, folding = discovery.find_frame(bits)
words = discovery.cut_words(bits, frame)
levels, pool, made_of, part_of = discovery.run_levels(words, 1, cap=1000000)
L0 = levels[0]            # runs, run_counts, run_follows, parts, endings, beginnings, classes

# the same thing, but against a saved memory
pool, made_of, part_of, history = discovery.load_memory('alice.memory')
levels, pool, made_of, part_of = discovery.run_levels(words, 1, 1000000, pool, made_of, part_of)
discovery.save_memory('alice.memory', pool, made_of, part_of, history + [('name', len(data), frame)])
```

## How long does it take

Pure Python. The text examples take seconds; the 1.6 MB AGC assembly
source, with its long runs and its very large record, takes the longest
of anything in the repo, well under a minute. For a big file, use
`--limit` to read just the first part, or split the file and run each
piece. The mint loop's time depends on how many distinct runs there are
and how long they are — not on file size — and writing the record
depends on how many connections were found. `--cap` (defaults to
1,000,000 parts) stops the mint loop if the pool gets too big, and the
record says so.
