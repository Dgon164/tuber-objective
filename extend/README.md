# Extensions

Discovery's basic comparison, which says whether two things are the
same, different, or one is part of the other, is called the comparator.
Each script in this folder points it at something new. None of them
changes `discovery.py`; each is a few lines that call it, and none
depends on another. Run whichever one you want.

Each script's output is committed in a file next to it, so you can read
the result before you run anything. Every script has the same three
sections:

- *the signal, as discovery.py reads it*: one call, `R = D.Root(path)`
- *NEW: the one new thing*
- *what it found*

Read the NEW section; the rest is the same program every time.
`guides/building-from-discovery.md` is the long explanation of why
these three sections are all a script needs.

| script | what it reads and what it does | command | what it writes |
|---|---|---|---|
| `template.py` | Reads `alice.txt`. This is the shape to copy: the three sections, with the middle one left empty for you to write. As it stands, it takes the most common repeating sequences and reports what tends to follow each one. | `python template.py ../examples/text/alice.txt` | Prints only. |
| `same_slot.py` | Reads `alice.txt`. For each repeating sequence it records the slot it sits in: the word on its left and the word on its right. Two sequences are "the same" in a slot when they appear between the same neighbours (`the ___ said`). What comes out is the parts of speech, with no labels. | `python same_slot.py ../examples/text/alice.txt` | `same_slot.output.txt` |
| `functions.py` | Reads `alice.txt` and a word list. Discovery records the changes that turn one part into another (`+ed` turns `walk` into `walked`). This script treats each change as a function and works out what kind of thing it acts on; two functions that are almost the same (siblings) take the same inputs. It uses those functions to build new English words from the record and checks them against the word list. `FUNCTIONS.md` is the full explanation. | `python functions.py ../examples/text/alice.txt [N] [WORDLIST]` | `alice.functions.txt`, and what the script printed, in `functions.output.txt` |
| `sentence.py` | Reads `alice.txt`. Discovery records which part follows which. This script chains those "what comes next" links from a starting part to an ending part, which makes a sentence. | `python sentence.py ../examples/text/alice.txt [N]` | `sentence.output.txt` (the script draws at random, so each run is different) |
| `cut_at_class.py` | Reads `alice.txt`. Cutting a signal means dividing it into pieces at a boundary. Discovery normally cuts the next level up at the most common repeating sequence; this script cuts it at the largest class instead, a class being a group of parts that take the same set of changes. | `python cut_at_class.py ../examples/text/alice.txt` | `cut_at_class.output.txt` |
| `same_within.py` | Reads the Apollo rope, the read-only program memory of the Apollo Guidance Computer, the computer that flew the Apollo spacecraft. It adds a new kind of "same": two words count as the same if they fall in the same band of 8. On the rope, a band stands for a nearby address. | `python same_within.py ../examples/agc/input/luminary099.rope` | `same_within.output.txt` |
| `row_by_row.py` | Reads the internal states of the neural net from `hybrid/net_as_lens.py`. It compares each row with the row before, keeps the fields that changed (the flips), and reads the flips as a new signal. | `python row_by_row.py ../hybrid/alice.txt.reservoir` (run `net_as_lens.py` first) | `row_by_row.output.txt`, `alice.txt.reservoir.flips.record.txt` |

Run each script from this folder; the paths above are relative to it.
`functions.py` needs a word list as its answer key,
`/usr/share/dict/american-english` by default. To use a different one,
give its path as the third argument.
