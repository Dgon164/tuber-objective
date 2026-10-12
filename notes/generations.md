# Generations of AI: a proposal

| Generation | Architecture | Defining characteristic |
|---|---|---|
| 1.0 | Human-made | Humans explicitly build the intelligence and write the rules it follows. |
| 1.1 | Human-made with self-refinement | Human-designed systems that can improve or tune themselves. |
| 2.0 | Neural networks | The system learns its own internal representations through training. |
| 2.1 | Hybrid | Neural approaches combined with other techniques, like symbolic reasoning. |
| 3.0 | Self-assembling and learning | The system discovers and builds its own representations, relationships, and knowledge from scratch. |

## Where this repo sits

Discovery is a 3.0 system by the definition in the table: nothing in it
is given a representation up front. It gets handed raw bits and a
comparator (a tool that checks "same or different?"), and everything
else -- the word size, the words, the parts, the classes, the levels,
the arrows, the effects -- gets built by the system from the signal it
receives (design rule 7: define nothing; `paper/discovery.md`). The
records are the evidence.

The `hybrid/` folder is where 3.0 meets 2.0 and 1.x: a neural net
feeding into Discovery (`net_as_lens.py`), Discovery feeding into a rule
table (`record_to_rules.py`), and a loop that passes one through the
other and back. `notes/on-the-bitter-lesson.md` explains why the path
from 2.0 to 3.0 is the Bitter Lesson taken to its conclusion: the human
knowledge that 2.0 systems still carry (baked into the loss function,
the action space, and the architecture) gets removed, and knowledge
becomes what comes out rather than what goes in.
