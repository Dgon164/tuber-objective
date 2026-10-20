# Generations of AI: a proposal

| Generation | Architecture | Definition |
|---|---|---|
| 1.0 | Human-made | Humans make the intelligence directly and write the rules that the intelligence obeys. |
| 1.1 | Human-made with self-refinement | Systems that humans designed and that can improve or tune themselves. |
| 2.0 | Neural networks | The system learns its own internal representations in the training step. |
| 2.1 | Hybrid | Neural methods in combination with other methods, for example symbolic reasoning. |
| 3.0 | Self-assembly and learning | The system finds and makes its own representations, relations, and knowledge from nothing. |

## The place of this repository

Discovery is a 3.0 system by the definition in the table. Discovery receives no representation at the start. Discovery gets the raw bits and a comparator. A comparator is a tool that checks if 2 things are the same or different. The system makes all other things from the signal that the system receives (see design rule 7, define nothing, and `paper/discovery.md`). The other things are:

- the word width
- the words
- the parts
- the classes
- the levels
- the arrows
- the effects

The records are the evidence.

The `hybrid/` folder is the place where 3.0 meets 2.0 and 1.x. The folder has 3 scripts:

- a neural net that gives its output to Discovery (`net_as_lens.py`)
- a script that gives the record of Discovery to a rule table (`record_to_rules.py`)
- a loop that passes the output of each system through the other system and back

`notes/on-the-bitter-lesson.md` explains why the path from 2.0 to 3.0 is the last step of the Bitter Lesson. The 2.0 systems still carry human knowledge in the loss function, the action space, and the architecture. The path from 2.0 to 3.0 removes that human knowledge. Knowledge becomes what comes out, not what goes in.
