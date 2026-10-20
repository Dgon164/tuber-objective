# On the Bitter Lesson

Richard Sutton wrote *The Bitter Lesson* in 2019. Its argument is simple. Methods that run on raw computation, searching through possibilities and learning from data, always end up beating methods built on what humans know. The history of AI, he says, is a history of researchers putting their own knowledge into a system, and then watching a simpler system go past it, because the simpler one searches more and learns more.

Discovery is what you get when you take that argument all the way to the end.

## No human knowledge at all

Even Sutton's own examples still contain human choices. Someone decides what kind of problem the system is solving. Someone decides the form of the reward, the score that tells the system when it did well. Someone decides what kinds of things the search is allowed to consider. There's less human knowledge than before, but it's still there, in three places: the measure of how wrong an answer is, which people choose; the set of moves the system can make, which people choose; and the shape of the system, which people choose.

Discovery takes all of that out.

It doesn't know what kind of file it's reading. It has no dictionary, no grammar, no list of machine instructions, and no table of file formats. It doesn't know whether the signal is text, code, or instructions for a machine. It doesn't even know how many bits make one unit. It works that out first, from the raw bits: it tries one width after another, lays the bits out in rows of that width, and looks for the width where some column barely changes from one row to the next. That's where the units line up.

The only thing Discovery is given is the comparator: a piece of code that takes two things and answers same, different, or not part of each other. That isn't human knowledge about the subject matter. It's the operation itself, and it's the smallest possible unit of learning: a yes-or-no comparison, one bit of answer. That one operation runs again and again on what it found the time before. Everything else assembles itself out of it: the parts the file is made of, the connections between them, the groups of parts that behave alike, and the levels where the whole thing is done again one step up.

## Three statements, each taken to its end

**Wheeler: "It from bit."** The system starts from raw bits and makes structure out of them. The bits are not a figure of speech. The system reads real bits from the file and compares them one column at a time. The "it" is the parts, the words, the groups, and the changes that turn one word into another, and all of it comes from nothing but the pattern of where the bits agree.

**Bateson: "A difference that makes a difference."** The comparator finds the differences, and the memory keeps them. A difference that shows up again is a difference that makes a difference: the same part turning up in another place, or the same ending fitting onto many words. A difference that never shows up again is noise. That's the only filter in the whole system, and it's nothing more than the comparator run on its own earlier output.

**Sutton: "General methods that leverage computation ultimately win."** Discovery uses one method on every file it has ever been given: compare, and remember. With that one method it found:

- 8-bit ASCII in English text, where every character is one byte
- 15-bit packed words in Apollo flight code, where the machine's units are 15 bits long and don't line up with bytes
- 64-bit words in a compiled binary, a program turned into machine code
- UTF-8 lead bytes in German, the byte that always comes before an accented letter

It used the same one file of Python, the same comparator, and the same loop every time. It has no special case for any of them. The computation is the method.

## What's left when all the human knowledge is gone

When you take the human knowledge about the subject out, you don't get a worse system that needs more data to make up the difference. You get a system that finds things a human wouldn't have thought to look for.

Discovery found that the instruction EXTEND is the separator in the Apollo Guidance Computer's code. The separator is the most common unit in a file, and it's what divides the file into stretches that mean something on their own. Nobody told Discovery what EXTEND does. Nobody told it what an instruction is.

It found that role from the same property that makes the space the separator in English: the separator is whatever shows up most often. To cut a signal is to divide it into stretches at every copy of the separator, and a cut at the most common thing gives the most structure.

That result is the bitter lesson in its purest form. The lesson isn't "search beats knowledge". That version still assumes knowledge is the thing you'd rather have, if only you could get it. The lesson is that knowledge is what you're left with when the search is finished. Knowledge is the output, not the input.
