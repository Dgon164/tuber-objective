# How to run Discovery

You need Python 3. There is nothing to install. Note:
`hybrid/net_as_lens.py` needs numpy. `extend/functions.py` needs a word
list. No other script needs anything.

## Run Discovery on a file

1. Run the command below, with the path of your file in place of FILE.

```
python discovery.py FILE
```

2. Read the 2 files that the program writes next to the input:
   - `FILE.record.txt`, the text record that people can read
   - `FILE.record.json`, the JSON record that programs can read

The program also prints the text record on your screen. When you use
`--frame` or `--separators`, the file names include the option. Thus
the records from different options on the same file do not replace
each other (for example `FILE.frame8.record.txt` or
`FILE.sep2.record.txt`). With `--memory`, the name includes `.mN`. N is
the count of signals that the memory has seen after the program adds
this signal.

## Options

| option | what the option does | default |
|---|---|---|
| `--lens raw\|ascii\|utf8\|octal` | how the record shows the words (the option changes the look, not the results) | `raw` (hex) |
| `--limit BYTES` | read only the first BYTES of the file | the whole file |
| `--widest BITS` | the widest word width to test | 64 |
| `--frame BITS` | skip the frame step (the search for the word width) and use this width | the width that the frame step finds |
| `--separators N` | use the N most common words as separators, not only 1 | 1 |
| `--separators HEX,HEX` | select the separator words yourself, in hex (`20,0a` means space and newline). For 1 word, write `0x20` or `20,`, because the program reads digits alone as a count | |
| `--cap PARTS` | stop the mint loop if the pool becomes larger than PARTS | 1000000 |
| `--memory FILE` | load the pool from FILE, compare this signal with the pool, then save the new pool back to FILE (JSON). A memory holds only signals that the program read at 1 frame | none |
| `--top N` | the number of rows to show for each table in the text record | 25 |
| `--out DIR` | the folder for the record files | next to the input |
| `--quiet` | do not print the record on the screen | |

The JSON record always has everything. The option `--top` changes only
the text output. The program finds the frame from the first 64 KB of
the file. If you give an option that the program does not know, you get
an error message. If you omit the value of an option, you also get an
error message. You do not get a wrong result in silence.

## The examples

Run the command for 1 example:

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

No example depends on a different example. The BREAKDOWN.md in the
folder of the example explains what to look for in the record that the
example writes. The script `run_examples.sh` is optional. The script
does all of the commands above, plus the extensions and the hybrid
scripts. The script makes each record in the repository again.

## Use Discovery from Python

```python
import discovery
R = discovery.Root('some/file', lens='ascii')   # the signal as read: R.words, R.frame, R.L0, R.pool, R.part_of
R.all_levels()                                  # every level, as discover() runs them: R.levels
txt, js = discovery.discover('some/file', lens='ascii', quiet=True)   # Root plus the record written
```

`Root` is the start point for each program made on Discovery. Each
script in `extend/` is `Root` plus 1 new thing. `discover()` also
starts from `Root`. You can also call the steps 1 at a time. Each step
is a plain function:

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

## The time that the program takes

The program is pure Python. The text examples take seconds. The 1.6 MB
AGC assembly source has long runs and a large record. This file takes
the longest time of all files in the repository. The time is much less
than 1 minute.

For a large file, use `--limit` to read only the first part. Or divide
the file into smaller files and run each smaller file.

The time of the mint loop depends on the number of different runs and
on the length of the runs. The time does not depend on the file size.
The time to write the record depends on the number of connections that
the program found. The option `--cap` (the default is 1,000,000 parts)
stops the mint loop if the pool becomes too large. The record then says
so.
