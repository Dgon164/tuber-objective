# The Tuber Objective

*A principle for root cause discovery*

> "It from bit."
> -- John Archibald Wheeler, 1990

> "Information is a difference that makes a difference."
> -- Gregory Bateson, *Steps to an Ecology of Mind*, 1972

This program applies the two quotations above directly.

The program reads a file as bits. The bits are the "bit". The program
compares the bits. The program finds what is the same and what is
different. From the comparisons, the program makes a record of each part
and each relation that the program finds. The record is the "it". You do
not tell the program what to find. The structure appears from the
comparison alone. A difference that occurs many times is important. A
difference that occurs one time is noise. This is the only rule. The
program applies this rule at each level.

One comparison operation. One memory. One Python file. No dependencies.

```
python discovery.py examples/text/alice.txt --lens ascii
```

## What the program does

Give the program a file. The file can be a novel, a compiled program, or
flight software from 1969. The program reads the raw bits. The program
finds the word width without help. The program finds the parts. The
program writes a record of each part. The record shows:

- what each part contains
- what contains each part
- what occurs next to each part
- what comes after each part, and the direction of the sequence
- the change that makes one part into a different part

The program has no list of file types, no dictionary, no grammar, and no
training step. The same program reads each of the 4 example files and
writes a record of each file. The records are the evidence. The code is
the explanation.

When the program operates correctly, the first lines of the output are
as follows:

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

The output shows 3 results. The word width is 8 bits, which is 1 ASCII
byte. There are 73 different characters in 144,395 characters. The
program minted 15,980 shared parts at level 0. To mint a part is to make
a new part from 2 parts that have the same start or the same end. Later
in the output, the record shows the space character as the separator.
The record shows a group of 22 verb stems. Each stem accepts the endings
`+ed` and `+ing`. The record shows entries such as `walk`, with `walked`
and `walking` as its forms.

## What the program found in 4 different signals

| input | word width found | separator found | record contents |
|---|---|---|---|
| English novel (ASCII text) | 8 bits. The top bit is never 1. | the space character | 73 letters and symbols in order of frequency, the words, the endings `+ed` and `+ing`, a group of 22 verb stems that accept both endings |
| German parliament debate (UTF-8 text) | 8 bits. The top bit is 1 in 3.6 percent of words. | the space character | a byte that occurs only before 4 other bytes (the umlaut lead byte), the endings `+en` `+ung` `+lich`, the prefixes `be+` `ge+`, 52 verb stems, 42 adjective stems |
| compiled C program (binary) | 64 bits, with a little-endian decrease in the column rates. At 8 bits, the text strings. | the zero word or zero byte | the layout of the file, the source file name `hello.c`, the functions `strlen` and `puts`, the usage message, the compiler version, the loader path |
| Apollo Guidance Computer flight code (packed 15-bit) | 15 bits. The program first picked 60. Then the program found that 60 is 15 repeated 4 times, and folded down to 15. | EXTEND (the instruction prefix, word 00006) | the true word width of the machine, the most common instruction sequences `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG`, each with its argument codes, and `RETURN` as the part with the most connections |

## Contents of the repository

| folder | contents |
|---|---|
| [`discovery.py`](discovery.py) | the full program, in 10 numbered sections, in 1 file |
| [`paper/discovery.md`](paper/discovery.md) | what the system is and why the system has this design |
| [`paper/persistence.md`](paper/persistence.md) | a proposed alignment paper. A root-cause objective is an objective under which complex things continue. The objective needs the complex things, cannot replace the complex things, and responds to harm at the cause of the harm (the baby model). |
| [`guides/`](guides/) | how to run the program, how the program operates step by step, how to read the record, how to give the program any signal, how to connect the program to other systems, and how to make new things on top of the program |
| [`notes/`](notes/) | the design rules, ideas not yet tried, a proposal for the generations of AI and the place of this program in them, and a log of what was made and when |
| [`examples/text/`](examples/text/BREAKDOWN.md) | an English novel (Alice in Wonderland, plain ASCII). The record shows the alphabet, the words, the word endings, and a group of 22 verb stems. |
| [`examples/german/`](examples/german/BREAKDOWN.md) | one day of the German parliament (UTF-8) and the English version, and a bridge that shows what the 2 languages share |
| [`examples/code/`](examples/code/BREAKDOWN.md) | the source code of Discovery, and a compiled C program read in 2 ways: as 64-bit words (the layout of the file) and as bytes (the text strings in the file) |
| [`examples/agc/`](examples/agc/BREAKDOWN.md) | the Apollo 11 Lunar Module flight software. The words are packed 15-bit words from a machine of the 1960s. The assembly source code is included. |
| [`examples/agc-live/`](examples/agc-live/README.md) | the same flight program in operation on an emulator of its machine. Each memory write and each hardware signal is recorded as a new signal for Discovery to read. The example builds and runs with 2 commands. |
| [`examples/memory/`](examples/memory/BREAKDOWN.md) | what occurs when Discovery keeps a memory: the first half of Alice with no memory, the second half with that memory, the second half again (the program learns nothing new), then German against the English memory |
| [`extend/`](extend/README.md) | extensions that get new results when they point the comparison at a new thing, with no change to the core: slot-mates (approximately the parts of speech), functions (words made from the record), and sentences made from the table of what follows what |
| [`hybrid/`](hybrid/README.md) | 3 scripts that connect Discovery to other systems: a rule engine, a neural net, and a loop that gives the output of Discovery back to Discovery |

Each example folder has the input file, the record that Discovery wrote,
and a BREAKDOWN.md that explains the record table by table. When an
outside source exists, the BREAKDOWN.md shows how to check the work of
Discovery against that source.

## Run one example

Select an example from the table. The BREAKDOWN.md of each example starts
with the command that makes its record. The record is in the same folder
as the input. You can read the record before you run the command. You can
also read the record and not run the command. Each extension and each
hybrid script has its command in its first lines and in the README of its
folder. No script depends on a different script, unless the script says
so. The hybrid loop reads a JSON record. The row-by-row extension reads
what the net wrote.

```
python discovery.py examples/text/alice.txt --lens ascii
```

From Python, the same operation is 1 call: `R = discovery.Root(path)`.
The call gives the signal as read, level 0, and the pool. Each program
made on Discovery in this repository is that call and 1 new idea. The
file `discovery.py` is also that call and 1 new idea.

## Make all records again

```
./run_examples.sh
```

This step is optional. The script makes each record and each output in
the repository again from the inputs, in 1 run. The script makes sure
that the committed records agree with what the code makes. The plain-text
records are committed. The JSON records are large, so the script or the
single commands above make them. The hybrid scripts and the bridge read
the JSON records. The script `hybrid/net_as_lens.py` needs numpy. The
script `extend/functions.py` needs a word list. The default word list is
`/usr/share/dict/american-english`. No other script needs anything. The
script omits a step when the thing that the step needs is not present.

## Sources of the input files

- `examples/text/alice.txt`: *Alice's Adventures in Wonderland*, 1865,
  public domain, from the NLTK Gutenberg sample.
- `examples/german/ep-00-01-17.*`: Europarl parallel corpus sample, as
  shipped with NLTK. See `examples/german/EUROPARL-README`.
- `examples/agc/input/Luminary099.binsource` and the `.agc` source:
  Virtual AGC project (virtualagc.org), public domain.
- `examples/code/input/hello.c`: written for this repository.

## Licence

The licence for all work written for this repository is MIT. See
`LICENSE`. Work from other sources keeps its own terms. Each source has
the least restrictive terms that apply:

- `examples/agc-live/virtualagc/yaAGC/`, `yaYUL/`, and `Tools/` are the
  Virtual AGC emulator and assembler. The licence is GPL version 2 or
  later. See `examples/agc-live/virtualagc/COPYING`. The file
  `discovery-trace.patch` changes these files, so a build of the patched
  emulator is also GPL.
- The Apollo flight program, Alice, and `hello.c` are public domain or
  written here. The Europarl sample: see `examples/german/EUROPARL-README`.

## Contact

Jason Weeks -- thetuberobjective@gmail.com. Write to this address or open
an issue here for a question, a thing you made on Discovery, a thing
Discovery got wrong, or a thing you need help with. The author wants to
know.
