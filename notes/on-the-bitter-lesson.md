# On the Bitter Lesson

Richard Sutton wrote *The Bitter Lesson* in 2019. The essay makes a simple argument. Methods that use raw computation (search and learning) always win against methods that use human knowledge. The history of AI is a history of researchers who put what they know into systems. Then the researchers see simpler methods go past those systems. The simpler methods search more and learn more.

Discovery is the result when you take that argument to its end.

## No human knowledge at all

The examples of Sutton still include some human choices:

- the type of problem
- the form of the reward signal
- the representations that the search covers

The human knowledge is less, but the human knowledge remains. The human knowledge is in the loss function, the action space, and the architecture. The loss function is the thing that tells the system what "good" means. The action space is the set of moves that the system can make. The architecture is the shape of the system.

Discovery removes all of that human knowledge.

Discovery does not know the type of the file that Discovery reads. Discovery has no dictionary, no grammar, no instruction set, and no file format table. Discovery does not know if the signal is text, code, or machine instructions. Discovery does not know the word width. Discovery finds the word width first, from the raw bits. To find the word width, Discovery looks for the column that changes least.

The only thing that Discovery gets is the comparator: same, different, not part. The comparator is not human knowledge about the domain. The comparator is the operation itself. The comparator is the smallest possible unit of learning: a yes/no comparison, 1 bit of resolution. That 1 operation runs again and again on what the operation found before. All other things assemble themselves from that 1 operation: the parts, the connections, the classes, and the levels.

## The 3 statements, each to its end

**Wheeler: "It from bit."** The system starts from raw bits and makes structure. The bits are not a metaphor. The system reads real bits from the file. The system compares the bits 1 column at a time. The "it" is the parts, the words, the classes, and the changes. The "it" comes only from the pattern of agreement between the bits.

**Bateson: "A difference that makes a difference."** The comparator finds the differences. The memory keeps the differences. A difference that occurs again is a difference that makes a difference. Examples are the same part that appears again, and the same change that applies to many words. A difference that does not occur again is noise. This rule is the only filter, and the filter is the comparator at work on its own output.

**Sutton: "General methods that leverage computation ultimately win."** Discovery uses 1 method on each signal that Discovery has received. The method is: compare and remember. Discovery found:

- 8-bit ASCII in English text
- 15-bit packed words in Apollo flight code
- 64-bit words in a compiled binary
- UTF-8 lead bytes in German

Discovery uses the same 1 file of Python, the same comparator, and the same loop. Discovery has no specialization. The computation is the method.

## The result after the removal of all human knowledge

When you remove the human knowledge about the domain, the result is not a worse system that needs more data in place of the knowledge. The result is a system that finds things that a human does not think to look for.

Discovery found that the EXTEND instruction of the Apollo Guidance Computer is the separator. The separator is the most common word. The separator divides the signal into runs with meaning. Nobody told Discovery what EXTEND does. Nobody told Discovery what an instruction is.

Discovery found the role from the same property that makes the space the separator in English. The separator is the most common thing. To cut a signal is to divide the signal into runs at each copy of the separator. A cut at the most common thing gives the most structure.

That result is the bitter lesson in its pure form. The lesson is not "search beats knowledge". That statement still accepts that knowledge is the thing that you prefer to have. The lesson is that knowledge is what you get when the search is complete. Knowledge is the output, not the input.
