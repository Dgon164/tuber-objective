# Extensions

Each script here points the comparator at something new without changing
`discovery.py`. They are each just a few lines that call into it. They
are independent of each other -- run whichever one you want. The output
each one printed is saved beside it, so you can read before you run.

Every script has the same three sections: *the signal, as discovery.py
reads it* -- one call, `R = D.Root(path)` -- then *NEW: the one new
thing*, then *what it found*. Read the NEW section; the rest is the
same program.
`guides/building-from-discovery.md` is the longer version of why these
are all it takes.

| script | what it points the comparator at | run | writes |
|---|---|---|---|
| `template.py` | The shape to copy: the three sections, with the middle one left for you to write. As-is, it finds what follows the most common repeated sequences. | `python template.py ../examples/text/alice.txt` | prints only |
| `same_slot.py` | Where a repeated sequence sits: two sequences are "the same" in a slot when they appear between the same neighbors (`the ___ said`). That is parts of speech, with no labels given. | `python same_slot.py ../examples/text/alice.txt` | `same_slot.output.txt` |
| `functions.py` | What a change acts on: Discovery's changes become functions, similar functions (siblings) share inputs, and new English words are built from the record against a word list. `FUNCTIONS.md` is the full writeup. | `python functions.py ../examples/text/alice.txt [N] [WORDLIST]` | `alice.functions.txt`, and what it printed in `functions.output.txt` |
| `sentence.py` | The sequence: a chain of "what comes next" links from a starter to an ender. | `python sentence.py ../examples/text/alice.txt [N]` | `sentence.output.txt` (it draws at random, so each run differs) |
| `cut_at_class.py` | A new way to cut the signal: level 1 cut at the largest class instead of the most common repeated sequence. | `python cut_at_class.py ../examples/text/alice.txt` | `cut_at_class.output.txt` |
| `same_within.py` | A new kind of "same": on the Apollo rope, words within a band of 8 count as the same, so a band stands in for a nearby address. | `python same_within.py ../examples/agc/input/luminary099.rope` | `same_within.output.txt` |
| `row_by_row.py` | A row against the row before it: the reservoir states from `hybrid/net_as_lens.py`, turned into flips (what changed) and read as a new signal. | `python row_by_row.py ../hybrid/alice.txt.reservoir` (after `net_as_lens.py` has run) | `row_by_row.output.txt`, `alice.txt.reservoir.flips.record.txt` |

Run each from this folder; the paths above are relative to it.
`functions.py` needs a word list as its answer key -- the default is
`/usr/share/dict/american-english`; pass another as the third argument.
