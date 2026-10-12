# On the Bitter Lesson

Richard Sutton's *The Bitter Lesson* (2019) argues that methods
leveraging computation — search and learning — consistently outperform
methods leveraging human knowledge. The history of AI is a history of
researchers encoding what they know into systems, and then those systems
being surpassed by simpler methods that search harder and learn more.

Discovery is what happens when you take that argument to its logical
absolute.

## No human knowledge at all

Sutton's examples still assume human choices: what kind of problem it
is, what the reward signal looks like, what representations to search
over. The human knowledge is reduced, but it's still there — in the
loss function, in the action space, in the architecture.

Discovery removes all of it.

It does not know what kind of file it is looking at. It has no
dictionary, no grammar, no instruction set, no file format table. It
does not know whether the signal is text, code, or machine instructions.
It does not even know the word size — it finds that first, from the bits
themselves, by looking for the column that changes least.

The only thing given is the comparator: same, different, not part. That
is not human knowledge about the domain. That is the operation itself —
the smallest possible unit of learning, a boolean comparison, one bit of
resolution. Everything else — the parts, the connections, the classes,
the levels — self-assembles from that one operation run repeatedly on
what it already found.

## The three statements, taken to their ends

**Wheeler: "It from bit."** The system starts from raw bits and
produces structure. Not bit-as-metaphor: actual bits, read from the
file, compared one column at a time. The "it" — parts, words, classes,
changes — comes from nothing but the pattern of which bits agree with
which.

**Bateson: "A difference that makes a difference."** The comparator
finds differences. The memory holds them. A difference that recurs — the
same part showing up again, the same change applying to multiple
words — is a difference that makes a difference. A difference that
doesn't recur is noise. That is the only filter, and it is the
comparator itself, applied to its own output.

**Sutton: "General methods that leverage computation ultimately win."**
Discovery uses one method — compare and remember — on every signal it
has ever been given. It found 8-bit ASCII in English text, 15-bit
packed words in Apollo flight code, 64-bit chunks in a compiled binary,
and UTF-8 lead bytes in German. The same 726 lines of Python, the same
comparator, the same loop. No specialization. The computation is the
method.

## What's left after you remove everything

When you remove human knowledge about the domain, you do not get a
worse system that needs more data to compensate. You get a system
that finds things the human wouldn't have looked for.

Discovery found that the Apollo Guidance Computer's EXTEND instruction
is the separator — the most common word, the one that splits the signal
into meaningful runs. No one told it what EXTEND does. No one told it
what an instruction is. It found the role from the same property that
makes a space the separator in English: it's the most common thing, and
cutting there gives you the most structure.

That is the bitter lesson in its pure form. Not "search beats
knowledge" — that still concedes that knowledge is the thing you'd
prefer to have. The actual lesson is that knowledge is what you get
when the search is done. It's the output, not the input.
