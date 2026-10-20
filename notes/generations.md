# Generations of AI: a proposal

| Generation | How it is built | What that means |
|---|---|---|
| 1.0 | Written by people | People build the intelligence directly. They write the rules, and the system follows them. |
| 1.1 | Written by people, with self-adjustment | People design the system, and the system can then improve or tune its own settings as it runs. |
| 2.0 | Neural networks | The system works out its own internal way of standing for things during training, instead of being told what the things are. |
| 2.1 | Mixed | A neural network combined with other methods, for example a set of written rules the system can reason with. |
| 3.0 | Builds itself and learns | The system finds and makes its own way of standing for things, the relations between those things, and what it knows, starting from nothing. |

## Where this repository fits

By the definition in the table, Discovery is a 3.0 system. It's given no way of standing for things at the start. It gets the raw bits of a file and a comparator, which is a piece of code that takes two things and says whether they're the same or different. Everything else, the system makes for itself out of the signal it was given (see design rule 7, define nothing, and `paper/discovery.md`). The things it makes are:

- the word width: how many bits make one unit of the file
- the words: the file cut into units of that width
- the parts: the pieces that two or more stretches of the file share
- the classes: groups of parts that all take the same additions
- the levels: the same cutting and comparing done again with each stretch treated as a single unit
- the arrows: for a pair of things that show up in both orders, which order is the more common one
- the effects: what tends to show up after a thing more often than it shows up elsewhere

The records the program writes are the evidence for all of this.

The `hybrid/` folder is where 3.0 meets 2.0 and 1.x. It has three scripts:

- a neural net whose output is fed to Discovery (`net_as_lens.py`): the net reads a text, its internal state after each step is written out as bits, and Discovery reads those bits as a file
- a script that turns Discovery's record into a table of rules (`record_to_rules.py`): a second program never sees the file, only the record, and answers questions from the rules it builds
- a loop that passes the output of each system through the other and back again

`notes/on-the-bitter-lesson.md` explains why the step from 2.0 to 3.0 is the last step of the Bitter Lesson, the argument that methods built on computation beat methods built on human knowledge. A 2.0 system still carries human knowledge in three places: in the measure of how wrong an answer is, which people choose; in the set of moves the system is allowed to make, which people choose; and in the shape of the network, which people choose. The step from 2.0 to 3.0 takes that human knowledge out. Knowledge becomes what comes out of the system, not what goes in.
