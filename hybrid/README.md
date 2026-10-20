# Hybrid systems

This folder has 3 methods to connect Discovery to a different system. No
method changes `discovery.py`. No script depends on a different script.
The output of each script is in a file next to the script. The guide
`guides/hybrid-systems.md` explains all 3 methods step by step.

Each script has the same 3 sections as the scripts in `extend/`:

- *the record, as discovery.py wrote it* (or *the signal, as
  discovery.py reads it*)
- *NEW: the one new thing*
- *what it found*

| script | what the script reads and what the script does | command | what the script writes |
|---|---|---|---|
| `record_to_rules.py` | The script reads the JSON record of Discovery. Discovery is in front. The script makes a rule table from the record: what comes next, the forms of the same word, and the groups of the same kind. A second system can run the rule table without the original signal. | `python record_to_rules.py ../examples/text/alice.txt.record.json` | `record_to_rules.output.txt` |
| `net_as_lens.py` | The script reads the text. A neural net is in front. A reservoir reads the text. The reservoir is a simple network with random weights that do not change. The script writes the internal states of the reservoir as bits. Discovery reads the bits as a new signal. The script needs numpy. | `python net_as_lens.py ../examples/text/alice.txt` | `alice.txt.reservoir`, the record of `alice.txt.reservoir`, `net_as_lens.output.txt` |
| `loop.py` | The script reads the JSON record. The script is the loop. The record becomes rules. The rules make a new text. Discovery reads the new text. The script compares the 2 records (the collision). | `python loop.py ../examples/text/alice.txt.record.json` | `loop.output.txt`, `loop.collide.txt` |

Run each script from this folder. The 2 scripts that read a JSON record
need the JSON record before the run. The command `python ../discovery.py
../examples/text/alice.txt --lens ascii` writes the JSON record next to
the input. The JSON records are not in the repository, because the JSON
records are large.
