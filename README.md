# The Tuber Objective

*A root cause discovery principle*

> "It from bit."
> — John Archibald Wheeler, 1990

> "Information is a difference that makes a difference."
> — Gregory Bateson, *Steps to an Ecology of Mind*, 1972

This program is both of those statements taken literally.

It reads any file as raw bits — the "bit" — and from nothing but a
comparator (what is the same, what is different) builds a record of
every part and relationship it can find — the "it." Structure is not
defined in advance. It emerges from the comparison. A difference that
recurs is a difference that makes a difference; a difference that
doesn't recur is noise. That is the only test, and it is applied at
every level.

One comparator. One memory. One Python file, 726 lines, no
dependencies.

```
python discovery.py examples/text/alice.txt --lens ascii
```

## What it does

Give it any file — a novel, a compiled program, flight software from
1969 — and it reads the file as raw bits, figures out the word size on
its own, finds the parts, and writes down everything it learned: what
each part is made of, what contains it, what shows up next to it, what
comes after it and which way the order runs, and what you'd have to
change to turn one part into another.

There's no list of file types, no dictionary, no grammar rules, and no
training step. The same program reads all four example signals and
writes a record of each one. The records are the evidence; the code is
the explanation.

If it's working, the first few lines of output will look like this:

```
FRAME   ...
  picked width 8
  chosen width 8
  column rates at width 8:
    0.000 0.745 0.950 0.235 0.338 0.477 0.333 0.452

LEVELS   ...
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
```

It found word size 8 (one byte — ASCII), 73 distinct letters and symbols
out of 144,395 total, and minted 15,980 shared parts at level 0.
Further in, the separator is the space character, the classes table
shows a group of 22 verb stems that all take `+ed` and `+ing`, and the
crystal has entries like `walk` with `walked` and `walking` listed as
its forms.

## What it found on four different signals

| what we fed it | word size it found | separator it found | what it wrote down |
|---|---|---|---|
| English novel (ASCII text) | 8 bits — the top bit is never on | the space character | 73 letters and symbols in frequency order, the words, the endings `+ed` and `+ing`, a group of 22 verb stems that take both |
| German parliament debate (UTF-8 text) | 8 bits — the top bit is on 3.6% of the time | the space character | a byte that only ever shows up before four others (the umlaut lead byte), endings `+en` `+ung` `+lich`, prefixes `be+` `ge+`, 52 verb stems, 42 adjective stems |
| compiled C program (binary) | 64 bits with a little-endian fall-off; at 8 bits, the human-readable strings | the zero word / zero byte | the file's internal layout; the source file name `hello.c`, the functions `strlen` and `puts`, the usage message, the compiler version, the loader path |
| Apollo Guidance Computer flight code (packed 15-bit) | 15 bits — it first picked 60, then noticed 60 is just 15 repeated four times, and folded down | EXTEND (the instruction prefix, word 00006) | the machine's actual word size; the most common instruction sequences — `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG` — each followed by their argument codes; `RETURN` as the most connected part |

## What's in here

| folder | what's in it |
|---|---|
| [`discovery.py`](discovery.py) | the whole program — ten numbered sections, one file |
| [`paper/discovery.md`](paper/discovery.md) | what the system is and why it's built this way |
| [`paper/persistence.md`](paper/persistence.md) | a proposed alignment paper: a root-cause objective is one under which complex things persist — it needs them, cannot get them back, and answers a harm by satisfying its cause (the baby model) |
| [`guides/`](guides/) | how to run it, how it works step by step, how to read what it writes, how to feed it anything, how to connect it to other systems, and how to build new things on top of it |
| [`notes/`](notes/) | the design rules, the things we haven't tried yet, a proposal for the generations of AI and where this sits in them, and a log of what was built and when |
| [`examples/text/`](examples/text/BREAKDOWN.md) | an English novel (Alice in Wonderland, plain ASCII): how it finds the alphabet, the words, the word endings, and a group of 22 verb stems |
| [`examples/german/`](examples/german/BREAKDOWN.md) | a day of German parliament (UTF-8) plus the English version, and a bridge that lines up what the two languages share |
| [`examples/code/`](examples/code/BREAKDOWN.md) | Discovery's own source code, and a compiled C program read two ways — as 64-bit chunks (the file's layout) and as single bytes (the readable strings inside) |
| [`examples/agc/`](examples/agc/BREAKDOWN.md) | the Apollo 11 Lunar Module flight software: tightly packed 15-bit words from a machine built in the 1960s, plus the assembly source code |
| [`examples/agc-live/`](examples/agc-live/README.md) | the same flight program running on an emulator of its machine, with every memory write and every hardware signal recorded as a new signal for Discovery to read; builds and runs with two commands |
| [`examples/memory/`](examples/memory/BREAKDOWN.md) | what happens when Discovery remembers: first half of Alice from scratch, second half against that memory, second half again (learns nothing new), then German against the English memory |
| [`extend/`](extend/README.md) | extensions that show you can get new results by pointing the comparator somewhere new, without changing the core: slot-mates (parts of speech), functions (word-making from the record), and sentence-making from the follows table |
| [`hybrid/`](hybrid/README.md) | three working scripts that connect Discovery to other systems: a rule engine, a neural net, and a loop that feeds Discovery's output back into itself |

Each example folder has the input file, the record Discovery wrote, and
a BREAKDOWN.md that walks through the record table by table — and where
an outside source exists, shows how to check Discovery's work against it.

## Run one

Pick anything in the table. Each example's BREAKDOWN.md opens with the
command that makes its record, and the record it made is committed next
to the input — so you can read first and run after, or never run at
all. Each extension and hybrid script carries its command in its first
lines and in its folder's README. None of them depends on another,
except where one says so (the hybrid loop reads a JSON record; the
row-by-row extension reads what the net wrote).

```
python discovery.py examples/text/alice.txt --lens ascii
```

From Python the same thing is one call — `R = discovery.Root(path)`:
the signal as read, level 0, the pool. Every program built on Discovery
in this repo is that call plus one new thing, and so is `discovery.py`
itself.

## Regenerate everything

```
./run_examples.sh
```

Optional. Rebuilds every record and output in the repo from the inputs
in one go, so that what is committed is what the code makes. The
plain-text records are committed; the JSON records (which the hybrid
scripts and the bridge read) are big, so they are built by this script
or by the single commands above. `hybrid/net_as_lens.py` needs numpy;
nothing else does.

## Where the input files come from

- `examples/text/alice.txt`: *Alice's Adventures in Wonderland*, 1865,
  public domain, from the NLTK Gutenberg sample.
- `examples/german/ep-00-01-17.*`: Europarl parallel corpus sample as
  shipped with NLTK; see `examples/german/EUROPARL-README`.
- `examples/agc/input/Luminary099.binsource` and the `.agc` source:
  Virtual AGC project (virtualagc.org), public domain.
- `examples/code/input/hello.c`: written for this repo.

## Licence

MIT. See `LICENSE`.

## Contact

Jason Weeks — thetuberobjective@gmail.com. Questions, something you
built on it, something it got wrong, something you'd like help with:
write, or open an issue here. I'd like to hear about it.
