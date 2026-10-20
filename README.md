# The Tuber Objective

*A root cause discovery principle*

> "It from bit."
> -- John Archibald Wheeler, 1990

> "Information is a difference that makes a difference."
> -- Gregory Bateson, *Steps to an Ecology of Mind*, 1972

This program takes those two quotes literally.

It reads any file as a string of bits. It compares the bits to each
other, over and over, and keeps a record of every repeated pattern it
finds and how those patterns relate to each other. You do not tell it
what to look for. If a difference shows up again and again, it matters.
If it shows up once, it is noise. That is the only rule, and the program
applies it at every level.

One comparison. One memory. One Python file. No dependencies.

```
python discovery.py examples/text/alice.txt --lens ascii
```

## What it does

Give it a file. The program works out how wide one unit is (a byte, a
15-bit word, a 64-bit word) by looking at which width makes the bit
patterns line up. It splits the file into those units and counts them.
The most common unit becomes the divider, the way a space divides words
in text, and the program cuts the file into chunks at every divider.

Then it compares the chunks. Two chunks that start the same way share a
part, and the program records that part and the two leftovers. It keeps
comparing until a pass finds nothing new. Then it treats each chunk as a
unit and does the whole thing again one level up, so it finds phrases
made of words the same way it found words made of letters.

What comes out is a record: every part it found, what each part is made
of, what each part is inside of, what tends to come before and after it,
and what you would add to one part to turn it into another. Parts that
take the same additions get grouped together, which is how 22 verb stems
end up in one group because they all take `+ed` and `+ing`.

There is no list of file types, no dictionary, no grammar, and no
training. The same program reads a novel, a compiled program, and 1969
flight software, and writes a record of each. The records are the
evidence. The code is the explanation.

When it runs, the first lines of output look like this:

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

That says: the unit is 8 bits wide (one byte, which is ASCII), there are
73 different characters in 144,395 total, and the program found 15,980
shared parts at the first level. Further down, the record names the
space as the divider, lists the words, and shows a group of 22 verb
stems with entries like `walk` that list `walked` and `walking` as its
forms.

## What it found in four different files

| what went in | unit width it found | divider it found | what it recorded |
|---|---|---|---|
| an English novel (plain ASCII text) | 8 bits, with the top bit never used | the space | 73 letters and symbols in frequency order, the words, the endings `+ed` and `+ing`, and a group of 22 verb stems that take both |
| a German parliament debate (UTF-8 text) | 8 bits, with the top bit used 3.6% of the time | the space | the byte that always comes before an umlaut, the endings `+en` `+ung` `+lich`, the prefixes `be+` `ge+`, 52 verb stems, 42 adjective stems |
| a compiled C program (binary) | 64 bits for the file layout, 8 bits for the readable text inside it | the zero word or zero byte | the file's internal structure, the source file name `hello.c`, the functions `strlen` and `puts`, the usage message, the compiler version, the loader path |
| Apollo 11 flight software (packed 15-bit words) | 15 bits. It first picked 60, then noticed 60 is 15 repeated four times, and settled on 15. | EXTEND, the instruction prefix | the machine's true word size, the most common instruction sequences `TC BANKCALL`, `TC INTPRET`, `TC PHASCHNG` with their argument codes, and `RETURN` as the most connected part |

## What is in the repository

| folder | what it is |
|---|---|
| [`discovery.py`](discovery.py) | the whole program, in ten numbered sections, in one file |
| [`paper/discovery.md`](paper/discovery.md) | what the system is and why it is built this way |
| [`paper/persistence.md`](paper/persistence.md) | a proposed alignment argument: a system whose only job is finding root causes keeps complex things alive, because it needs them, cannot replace them, and fixes harm at the cause rather than the symptom. The baby model is the example. |
| [`guides/`](guides/) | how to run it, how it works step by step, how to read what it writes, how to feed it any kind of file, how to connect it to other systems, and how to build new things on it |
| [`notes/`](notes/) | the design rules, ideas not tried yet, a proposal for where this fits among generations of AI, and a log of what was built and when |
| [`examples/text/`](examples/text/BREAKDOWN.md) | Alice in Wonderland. How the program finds the alphabet, the words, the word endings, and the 22 verb stems. |
| [`examples/german/`](examples/german/BREAKDOWN.md) | a day of German parliament plus the English translation, and a bridge script that lines up what the two languages share |
| [`examples/code/`](examples/code/BREAKDOWN.md) | the program's own source, and a compiled C program read two ways: as 64-bit units for the layout and as bytes for the text inside |
| [`examples/agc/`](examples/agc/BREAKDOWN.md) | the Apollo 11 Lunar Module flight software, in the original packed 15-bit format, plus its assembly source |
| [`examples/agc-live/`](examples/agc-live/README.md) | the same flight software actually running on an emulator, with every memory write and hardware signal recorded as a new file for the program to read. Builds and runs with two commands. |
| [`examples/memory/`](examples/memory/BREAKDOWN.md) | what happens when the program remembers. First half of Alice from scratch, second half using that memory, second half again (it learns nothing new), then German against the English memory. |
| [`extend/`](extend/README.md) | short scripts that get new results by pointing the comparison somewhere new, without changing the core: parts of speech, building words from the record, making sentences from what follows what |
| [`hybrid/`](hybrid/README.md) | three scripts that connect the program to other systems: a rule engine, a neural net, and a loop that feeds its own output back in |

Each example folder has the input file, the record the program wrote,
and a BREAKDOWN.md that walks through the record table by table. Where
an outside source exists, the breakdown shows how to check the program's
work against it.

## Run one

Pick anything from the table. Each example's BREAKDOWN.md opens with the
command that makes its record, and the record is committed next to the
input, so you can read first and run later, or never run at all. The
extension and hybrid scripts each have their command in their first
lines and in their folder's README.

```
python discovery.py examples/text/alice.txt --lens ascii
```

From Python it is one call, `R = discovery.Root(path)`, which gives you
the file as units, the first level of parts, and the shared pool. Every
program built on this in the repository is that call plus one new idea.

## Regenerate everything

```
./run_examples.sh
```

Optional. Rebuilds every record from its input so that what is
committed matches what the code produces. The plain-text records are
committed. The JSON records are large, so this script (or the single
commands above) builds them. `hybrid/net_as_lens.py` needs numpy and
`extend/functions.py` needs a word list (`/usr/share/dict/american-english`
by default). Nothing else needs anything, and the script skips a step
when what it needs is not there.

## Where the input files come from

- `examples/text/alice.txt`: *Alice's Adventures in Wonderland*, 1865,
  public domain, from the NLTK Gutenberg sample.
- `examples/german/ep-00-01-17.*`: Europarl parallel corpus sample as
  shipped with NLTK. See `examples/german/EUROPARL-README`.
- `examples/agc/input/Luminary099.binsource` and the `.agc` source:
  Virtual AGC project (virtualagc.org), public domain.
- `examples/code/input/hello.c`: written for this repository.

## Licence

MIT for everything written for this repository. See `LICENSE`. Anything
brought in from elsewhere keeps its own terms, the loosest each has:

- `examples/agc-live/virtualagc/yaAGC/`, `yaYUL/` and `Tools/`, the
  Virtual AGC emulator and assembler: GPL version 2 or later, see
  `examples/agc-live/virtualagc/COPYING`. `discovery-trace.patch`
  modifies them, so a build of the patched emulator is GPL as well.
- The Apollo flight program, Alice, and `hello.c`: public domain, or
  written here. The Europarl sample: `examples/german/EUROPARL-README`.

## Contact

Jason Weeks -- thetuberobjective@gmail.com. Questions, something you
built on it, something it got wrong, something you want help with:
write, or open an issue here.
