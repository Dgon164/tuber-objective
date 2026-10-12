# Extensions

Each script here points the comparator somewhere new without changing
`discovery.py`; each is a few lines that call into it. They are
independent of one another — run the one you want. The output each one
printed is committed beside it, so you can read before you run.

Every script has the same three sections: *the signal, as discovery.py
reads it* — one call, `R = D.Root(path)` — then *NEW: the one new
thing*, then *what it found*. Read the NEW section; the rest is the
same program.
`guides/building-from-discovery.md` is the long version of why these
are enough.

| script | what it points the comparator at | run | writes |
|---|---|---|---|
| `template.py` | the shape to copy: the three sections, with the middle one left to write (as it stands: for the most common runs, what follows them) | `python template.py ../examples/text/alice.txt` | prints only |
| `same_slot.py` | where a run stands: two runs are the same in a slot when they sit between the same neighbours (`the ___ said`); parts of speech, with no labels given | `python same_slot.py ../examples/text/alice.txt` | `same_slot.output.txt` |
| `functions.py` | what a change acts on: Discovery's changes become functions, siblings are functions sharing inputs, and new English words are made from the record against a word list (`FUNCTIONS.md` is the writeup) | `python functions.py ../examples/text/alice.txt [N] [WORDLIST]` | `alice.functions.txt`, and what it printed in `functions.output.txt` |
| `sentence.py` | the sequence: a chain of follows from a starter to an ender | `python sentence.py ../examples/text/alice.txt [N]` | `sentence.output.txt` (it draws at random, so each run differs) |
| `cut_at_class.py` | a new cut: level 1 cut at the largest class instead of the most common run | `python cut_at_class.py ../examples/text/alice.txt` | `cut_at_class.output.txt` |
| `same_within.py` | a new kind of same: on the Apollo rope, words in the same band of 8 count as the same, so a band stands in the slot of a nearby address | `python same_within.py ../examples/agc/input/luminary099.rope` | `same_within.output.txt` |
| `row_by_row.py` | a row against the row before it: the reservoir states from `hybrid/net_as_lens.py`, their flips read as a new signal | `python row_by_row.py ../hybrid/alice.txt.reservoir` (after `net_as_lens.py` has run) | `row_by_row.output.txt`, `alice.txt.reservoir.flips.record.txt` |

Run each from this folder; the paths above are relative to it.
`functions.py` needs a word list as its answer key — the default is
`/usr/share/dict/american-english`; give another as the third argument.
