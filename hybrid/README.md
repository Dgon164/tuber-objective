# Hybrid systems

This folder has three ways to connect Discovery to another system. None
of them changes `discovery.py`, none depends on another, and each
script's output is committed in a file next to it. `guides/hybrid-systems.md`
walks through all three step by step.

Each script has the same three sections as the scripts in `extend/`:

- *the record, as discovery.py wrote it* (or *the signal, as
  discovery.py reads it*)
- *NEW: the one new thing*
- *what it found*

| script | what it reads and what it does | command | what it writes |
|---|---|---|---|
| `record_to_rules.py` | Reads the JSON record Discovery wrote. Here Discovery goes first and the other system comes after it. The script builds a rule table from the record: which chunk follows which, which chunks are forms of the same word, and which chunks are of the same kind. The data flows from Discovery to the rule table, and the other system can run on the rules without ever seeing the original text. | `python record_to_rules.py ../examples/text/alice.txt.record.json` | `record_to_rules.output.txt` |
| `net_as_lens.py` | Reads the text. Here a neural net goes first and Discovery comes after it. The net is a reservoir: a simple network with random connections that are never trained. The text is fed through it one byte at a time, and after each byte the script writes the net's internal state out as bits. Discovery reads those bits as a new signal, the net's view of the text. The data flows from the net to Discovery. Needs numpy. | `python net_as_lens.py ../examples/text/alice.txt` | `alice.txt.reservoir`, the record of `alice.txt.reservoir`, `net_as_lens.output.txt` |
| `loop.py` | Reads the JSON record. This one is a loop. The record becomes rules, the rules write a new text, Discovery reads the new text and writes a second record, and the script compares the two records: what both share, what the first had that the second lost, and what's new in the second. The script calls that comparison the collision. The data flows out of Discovery and back in. | `python loop.py ../examples/text/alice.txt.record.json` | `loop.output.txt`, `loop.collide.txt` |

Run each script from this folder. The two that read a JSON record need
it to exist first: `python ../discovery.py ../examples/text/alice.txt --lens ascii`
writes it next to the input. The JSON records aren't committed because
they're large.
