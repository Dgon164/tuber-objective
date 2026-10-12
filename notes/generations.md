# Generations of AI: a proposal

| Generation | Architecture | Defining characteristic |
|---|---|---|
| 1.0 | Human-made | Humans explicitly construct the intelligence and its operating rules. |
| 1.1 | Human-made with self-refinement | Human-designed systems can improve or refine themselves. |
| 2.0 | Neural networks | Learned representations emerge through neural-network training. |
| 2.1 | Hybrid | Neural approaches combined with other mechanisms, such as symbolic reasoning. |
| 3.0 | Self-assembling and learning | The system discovers and constructs its own representations, relationships, and knowledge structures. |

## Where this repo sits

Discovery is a 3.0 system by the definition in the table: nothing in it
is given a representation. It is handed bits and a comparator, and the
word size, the words, the parts, the classes, the levels, the arrows and
the effects are constructed by the system from the signal (design rule
7: define nothing; `paper/discovery.md`). The records are the evidence.

The `hybrid/` folder is where 3.0 meets 2.0 and 1.x: a net in front of
Discovery (`net_as_lens.py`), Discovery in front of a rule table
(`record_to_rules.py`), and the loop that feeds one back through the
other. `notes/on-the-bitter-lesson.md` says why the line from 2.0 to
3.0 is the Bitter Lesson taken to its end: the human knowledge that 2.0
still carries in the loss, the action space and the architecture is
removed, and knowledge becomes the output rather than the input.
