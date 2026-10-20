# How to run Discovery

You need Python 3, and there is nothing to install. Two of the extra
scripts have their own needs: `hybrid/net_as_lens.py` needs numpy, and
`extend/functions.py` needs a word list. No other script needs anything.

## Run Discovery on a file

1. Run the command below, with the path of your file in place of FILE.

```
python discovery.py FILE
```

2. Read the two files the program writes next to the input:
   - `FILE.record.txt`, the record written for people to read
   - `FILE.record.json`, the same record written for programs to read

The program also prints the text record on your screen. When you use
`--frame` or `--separators`, the option goes into the file name, so
records made with different options on the same file don't overwrite
each other (for example `FILE.frame8.record.txt` or
`FILE.sep2.record.txt`). With `--memory`, the name includes `.mN`,
where N is how many signals the memory has seen once this one is added
to it.

## Options

A few of the options refer to parts of the program by name. The frame
is the width of one unit of the file in bits, which the program works
out by itself unless you tell it. The separator is the most common
unit; the program cuts the file at every separator, and each piece
between two separators is a run. The program then compares the runs in
pairs and records every shared piece it finds in one list, the pool.
That comparison loop is the mint step. The lens is how the record
prints a unit on the page. A memory is a pool saved after one file and
loaded before the next.

| option | what it is for | default |
|---|---|---|
| `--lens raw\|ascii\|utf8\|octal` | how the record prints each unit: as hex, as the character, decoded as UTF-8, or in base 8. This changes only how the record looks, never the results. Use `ascii` for plain text, `utf8` for text with accented characters, and `octal` when the listing you are checking against is printed in base 8 | `raw` (hex) |
| `--limit BYTES` | read only the first BYTES of the file and ignore the rest. Use it to get a quick record of the start of a large file | the whole file |
| `--widest BITS` | the widest unit width the program will try when it searches for the frame. Raise it if the unit you want might be wider than 64 bits | 64 |
| `--frame BITS` | skip the search for the unit width and use this width instead. Use it to read the same file at a different width, for example a compiled program at 8 bits to see the text inside it rather than its 64-bit layout | the width the search finds |
| `--separators N` | cut runs at the N most common units rather than only at the single most common one. Use it when two or three different units divide the thing you want to see, such as space and newline | 1 |
| `--separators HEX,HEX` | choose the separator units yourself, in hex (`20,0a` means space and newline). For a single unit write `0x20` or `20,`, because the program reads digits on their own as a count | |
| `--cap PARTS` | stop the mint loop early if the pool grows past PARTS. This is a size limit, not a rule of the method; the record says so when it kicks in | 1000000 |
| `--memory FILE` | load the pool saved in FILE, compare this signal against it as well as against itself, then save the combined pool back to FILE as JSON. Use it to read a second file against what the first one taught the program. A memory can only hold signals read at one frame | none |
| `--top N` | how many rows to print for each table in the text record. Raise it to see more of a table on screen | 25 |
| `--out DIR` | the folder to write the record files into | next to the input |
| `--quiet` | don't print the record on the screen; only write the files | |

The JSON record always has everything, and `--top` changes only the
text output. The program finds the frame from the first 64 KB of the
file. If you give an option the program doesn't know, you get an error
message. If you leave out the value of an option, you also get an error
message. You never get a wrong result in silence.

## The examples

Run the command for one example:

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

No example depends on another. The BREAKDOWN.md in each example's
folder explains what to look for in the record that example writes.
The script `run_examples.sh` is optional: it runs all of the commands
above, plus the extension and hybrid scripts, and rebuilds every record
in the repository.

## Use Discovery from Python

```python
import discovery
R = discovery.Root('some/file', lens='ascii')   # the signal as read: R.words, R.frame, R.L0, R.pool, R.part_of
R.all_levels()                                  # every level, as discover() runs them: R.levels
txt, js = discovery.discover('some/file', lens='ascii', quiet=True)   # Root plus the record written
```

`Root` is the starting point for every program built on Discovery. Each
script in `extend/` is `Root` plus one new thing, and `discover()`
starts from `Root` too. You can also call the steps one at a time, since
each step is a plain function:

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

## How long it takes

The program is pure Python. The text examples take seconds. The 1.6 MB
AGC assembly source has long runs and a large record, and it takes the
longest of any file in the repository, which is still well under a
minute.

For a large file, use `--limit` to read only the first part, or split
the file into smaller files and run each one.

The time the mint loop takes depends on how many different runs there
are and how long they are, not on the size of the file. The time to
write the record depends on how many connections the program found.
The option `--cap` (the default is 1,000,000 parts) stops the mint loop
if the pool grows too large, and the record says so.
