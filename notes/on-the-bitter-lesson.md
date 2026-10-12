# On the Bitter Lesson

Richard Sutton's *The Bitter Lesson* (2019) makes a straightforward argument: methods that lean on raw computation -- search and learning -- consistently beat methods that lean on human knowledge. The history of AI is a history of researchers encoding what they know into systems, and then watching simpler methods that just search harder and learn more blow past them.

Discovery is what happens when you take that argument all the way to the end.

## No human knowledge at all

Sutton's examples still assume some human choices: what kind of problem it is, what the reward signal looks like, what representations to search over. The human knowledge is reduced, but it's still there -- baked into the loss function (the thing that tells the system what "good" means), the action space (the set of moves it can make), and the architecture (the shape of the system itself).

Discovery removes all of it.

It doesn't know what kind of file it's looking at. It has no dictionary, no grammar, no instruction set, no file format table. It doesn't know whether the signal is text, code, or machine instructions. It doesn't even know the word size -- it figures that out first, from the raw bits, by looking for the column that changes least.

The only thing it's given is the comparator: same, different, not part. That's not human knowledge about the domain. That's the operation itself -- the smallest possible unit of learning, a yes/no comparison, one bit of resolution. Everything else -- the parts, the connections, the classes, the levels -- self-assembles from that one operation run over and over on what it already found.

## The three statements, taken to their ends

**Wheeler: "It from bit."** The system starts from raw bits and produces structure. Not bit-as-metaphor: actual bits, read from the file, compared one column at a time. The "it" -- parts, words, classes, changes -- comes from nothing but the pattern of which bits agree with which.

**Bateson: "A difference that makes a difference."** The comparator finds differences. The memory holds them. A difference that comes back -- the same part showing up again, the same change applying to multiple words -- is a difference that makes a difference. A difference that doesn't come back is noise. That's the only filter, and it's just the comparator applied to its own output.

**Sutton: "General methods that leverage computation ultimately win."** Discovery uses one method -- compare and remember -- on every signal it has ever been given. It found 8-bit ASCII in English text, 15-bit packed words in Apollo flight code, 64-bit chunks in a compiled binary, and UTF-8 lead bytes in German. The same one file of Python, the same comparator, the same loop. No specialization. The computation is the method.

## What's left after you remove everything

When you remove human knowledge about the domain, you don't get a worse system that needs more data to make up for it. You get a system that finds things the human wouldn't have thought to look for.

Discovery found that the Apollo Guidance Computer's EXTEND instruction is the separator -- the most common word, the one that splits the signal into meaningful runs. Nobody told it what EXTEND does. Nobody told it what an instruction even is. It found the role from the same property that makes a space the separator in English: it's the most common thing, and cutting there gives you the most structure.

That's the bitter lesson in its pure form. Not "search beats knowledge" -- that still concedes that knowledge is the thing you'd prefer to have. The actual lesson is that knowledge is what you get when the search is done. It's the output, not the input.
