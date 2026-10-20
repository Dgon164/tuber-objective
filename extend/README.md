# Extensions

Each script in this folder points the comparator at a new thing. The
comparator is the tool of Discovery that finds differences. No script
changes `discovery.py`. Each script is a small number of lines that call
`discovery.py`. No script depends on a different script. Run the script
that you want.

The output of each script is in a file next to the script. Thus you can
read the output before you run the script. Each script has the same 3
sections:

- *the signal, as discovery.py reads it*: 1 call, `R = D.Root(path)`
- *NEW: the one new thing*
- *what it found*

Read the NEW section. The rest is the same program. The guide
`guides/building-from-discovery.md` is the long explanation of the
cause: these sections are all that a script needs.

| script | what the script reads and what the script does | command | what the script writes |
|---|---|---|---|
| `template.py` | The script reads `alice.txt`. The script is the shape to copy: the 3 sections, with the middle section empty for you to write. Without a change, the script finds what follows the most common sequences that repeat. | `python template.py ../examples/text/alice.txt` | The script prints only. |
| `same_slot.py` | The script reads `alice.txt`. The script finds the slot of each sequence that repeats. Two sequences are "the same" in a slot when the 2 sequences occur between the same neighbors (`the ___ said`). The result is the parts of speech, with no labels. | `python same_slot.py ../examples/text/alice.txt` | `same_slot.output.txt` |
| `functions.py` | The script reads `alice.txt` and a word list. The script finds what a change acts on. The changes of Discovery become functions. Functions that are almost the same (siblings) have the same inputs. The script makes new English words from the record and checks the words against the word list. The file `FUNCTIONS.md` is the full explanation. | `python functions.py ../examples/text/alice.txt [N] [WORDLIST]` | `alice.functions.txt`, and the output that the script printed, in `functions.output.txt` |
| `sentence.py` | The script reads `alice.txt`. The script makes a sequence: a chain of "what comes next" links from a start part to an end part. | `python sentence.py ../examples/text/alice.txt [N]` | `sentence.output.txt` (the script draws at random, so each run is different) |
| `cut_at_class.py` | The script reads `alice.txt`. To cut a signal is to divide the signal into parts at a boundary. The script cuts the signal in a new way. The level 1 cut is at the largest class, not at the most common sequence that repeats. | `python cut_at_class.py ../examples/text/alice.txt` | `cut_at_class.output.txt` |
| `same_within.py` | The script reads the Apollo rope. The rope is the read-only program memory of the Apollo Guidance Computer. The script uses a new kind of "same": words in a band of 8 count as the same. Thus a band stands for an address that is near. | `python same_within.py ../examples/agc/input/luminary099.rope` | `same_within.output.txt` |
| `row_by_row.py` | The script reads the reservoir states from `hybrid/net_as_lens.py`. The script compares each row with the row before. The script makes flips (the fields that changed) and reads the flips as a new signal. | `python row_by_row.py ../hybrid/alice.txt.reservoir` (run `net_as_lens.py` first) | `row_by_row.output.txt`, `alice.txt.reservoir.flips.record.txt` |

Run each script from this folder. The paths above are relative to this
folder. The script `functions.py` needs a word list as the answer key.
The default word list is `/usr/share/dict/american-english`. To use a
different word list, give the path as the third argument.
