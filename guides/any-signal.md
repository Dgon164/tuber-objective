# Feeding Discovery any signal

Discovery reads a file as raw bits. It doesn't have a list of file
types. The only question for a new kind of signal is: how do I get it
into a file, and at what chunk size does the thing I care about live?

## Things that are already files

Just run them. The frame step figures out the word size; the most common
word becomes the separator.

| signal | what the frame step usually finds | what the separator usually is |
|---|---|---|
| plain text (ASCII, UTF-8) | 8 | the space |
| source code | 8 | the space or the tab |
| a compiled program (x86-64) | 64 | the zero word; at `--frame 8`, the zero byte |
| a packed word-machine image | the machine's word size (15 for the AGC) | its most common instruction |
| a raw 16-bit audio file (.wav, .raw) | 16 or a multiple | the most common sample value |
| raw pixels (8-bit grey, RGB) | 8 or 24 | the most common pixel value |
| a CSV or log file | 8 | the comma, or the space |
| a fixed-record database file | the record width in bits, if under `--widest` | the padding byte |

Compressed or encrypted files (zip, png, jpeg, anything that looks
random) give a flat FRAME table and a word table where nothing repeats.
That's actually a correct reading: the signal has been scrambled on
purpose, and the frame step is right to report no structure. Decompress
first, then run on the contents.

## Things that aren't files yet

Write them as bytes. The one rule: write each reading the same way every
time, so the frame step has something to find.

- **A stream of numbers** (sensor readings, prices, a time series):
  write each as the same fixed-size integer. `struct.pack('<h', x)` for
  16-bit, `'<i'` for 32-bit. The frame step will find 16 or 32; the
  separator will be the most common value.
- **A state vector** (a neural net's activations, a simulation's
  variables): turn each value into a fixed number of bits and pack them
  in order. `hybrid/net_as_lens.py` does this with one bit per unit (the
  sign). With 8 bits per unit, each unit is a byte and a state is a row
  of bytes.
- **Events** (a log of things that happened): write each event as a
  fixed-size code. The run between separators is then an event sequence,
  and the FOLLOWS table becomes the transition table (what tends to
  happen after what).
- **An image**: write the pixels row by row, one byte per color channel.
  The frame step finds the pixel width. If the image width in bits is
  under `--widest`, a width equal to the row can also show up (one
  column per pixel position). For bigger images, raise `--widest`.

## Grain

The frame step picks the width where the columns differ the most.
That's the chunk size where the signal's bits are most organized --
which is usually, but not always, the chunk size you want to look at.
The compiled program is the prime example: at 64 bits the record is
about the file's internal layout; at `--frame 8` it's about the
human-readable strings and names. Both are true. When the record at the
auto-detected width doesn't show much, force the next natural size down
(`--frame 8`, `--frame 16`) and look again.

## Separators

The most common word is the separator. For a signal where the thing you
care about is split by two or three different words (space and newline;
tab and space; comma and newline), use `--separators N`. The record
tells you when this is the case: a word with a high density in PARTS BY
DENSITY and a zero whole count is acting like a separator that didn't
get picked.

## Size

The mint loop's cost depends on how many distinct runs there are and how
long they are -- not on the file size. A file with short, repeating runs
(text, code, machine words) finishes in seconds at a few hundred
kilobytes. A file with long, unique runs (a log where every line is
different, a binary read at the byte level) grows the pool faster;
`--cap` stops it and says so. Use `--limit` to read just the first part
of a large file, or cut the file into pieces and run them.
