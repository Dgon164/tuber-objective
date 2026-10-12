# Hybrid systems

Three ways to put Discovery next to another system. Nothing in
`discovery.py` changes for any of them; each script is independent of
the others. What each one printed is committed beside it.
`guides/hybrid-systems.md` walks through all three.

Each script has the same three sections as the ones in `extend/`: *the
record, as discovery.py wrote it* (or *the signal, as discovery.py reads
it*), *NEW: the one new thing*, and *what it found*.

| script | the wiring | run | writes |
|---|---|---|---|
| `record_to_rules.py` | Discovery in front: the record becomes a rule table (next-run, forms-of, same-kind) that a second system runs without ever seeing the signal | `python record_to_rules.py ../examples/text/alice.txt.record.json` | `record_to_rules.output.txt` |
| `net_as_lens.py` | a net in front: a fixed random reservoir reads the text, its states are written as bits, and Discovery reads that as a new signal (needs numpy) | `python net_as_lens.py ../examples/text/alice.txt` | `alice.txt.reservoir`, its record, `net_as_lens.output.txt` |
| `loop.py` | the loop: record → rules → a new text → Discovery again, and the two records collided | `python loop.py ../examples/text/alice.txt.record.json` | `loop.output.txt`, `loop.collide.txt` |

Run each from this folder. The two that read a JSON record need it
built first — `python ../discovery.py ../examples/text/alice.txt --lens
ascii` writes it next to the input (JSON records are not committed;
they are large).
