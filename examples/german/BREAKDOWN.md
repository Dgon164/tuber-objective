# Breakdown: German from the signal

## The input

The file `ep-00-01-17.de` is 1 day of the debate of the European Parliament (17 January 2000) in German. The file has 160,002 bytes. The file `ep-00-01-17.en` is the same day in English. The German file is UTF-8. In UTF-8, the letters a-umlaut, o-umlaut, u-umlaut, and sharp-s each use 2 bytes in place of 1 byte.

```
python discovery.py examples/german/ep-00-01-17.de --lens utf8
python discovery.py examples/german/ep-00-01-17.en --lens ascii
python bridge.py ep-00-01-17.de.record.json ep-00-01-17.en.record.json
```

The `utf8` lens shows whole runs as text that you can read. Thus the lens shows `a-umlaut` as the character and not as 2 hexadecimal codes. In the WORDS table, the lens shows single bytes one at a time. In the WORDS table, the 2-byte letters occur as pairs of bytes.

## FRAME: 8-bit words, with the top bit in use 3.6 percent of the time

```
    8    0.892   col   0 at 0.036   col   2 at 0.928
  chosen width 8
  column rates at width 8:
    0.036 0.803 0.928 0.245 0.315 0.494 0.377 0.462
```

The answer is the same as for the English text: 8 bits. But column 0 is not 0 this time. The top bit is 1 in 3.6 percent of the words. In Alice, column 0 was 0.000. This one number is enough to show the difference between this file and a pure 7-bit file.

## WORDS: 88 different words, with `\xc3`

```
WORDS   160002 words, 88 distinct
  00100000          23206
  01100101  e       20397
  01101110  n       13451
  01101001  i       11048
  01110010  r       9898
  ...
  11000011  \xc3    2827
```

The words that have the top bit at 1 are the bytes of the UTF-8 letters. The word `11000011` (`\xc3`) is the first byte of a-umlaut, o-umlaut, u-umlaut, and sharp-s. This word occurs 2,827 times. The FOLLOWS table shows that this word always occurs directly before 1 of 4 bytes. These 4 bytes are the 4 special letters.

The record does not know what UTF-8 is. The record shows only a byte that occurs only directly before 4 other bytes.

The letter order is e, n, i, r, t, s, d, a, h, u. In Alice, the letter order was e, t, a, o, h, n. The 2 languages have 2 different frequency orders. The process is the same for the 2 languages.

## RUNS: the German words

```
RUNS   23206 runs between separators, 4489 distinct
  ,             1702
  der            878
  die            862
  und            629
  in             376
  den            302
  zu             271
  dass           263
  fuer           248
  Kommission     125
```

The comma is a run on its own here, because the text puts a space on each side of the comma. The RUN FOLLOWS table shows the pairs:

- `, dass`, 244 times
- `, die`, 177 times
- `fuer die`, 81 times
- `in den`, 68 times
- `der Kommission`, 59 times
- `die Kommission`, 53 times
- `moechte ich`, 45 times
- `.\nHerr Praesident`, 42 times

## ENDINGS, BEGINNINGS, and CLASSES

```
ENDINGS               BEGINNINGS
  +n      1731           e+   987
  +en     1507           s+   765
  +e      1461           A+   317
  +t      1153           S+   313
  +s       855           E+   301
  +r       821          be+   293
  +ung     381          ge+   275
  +er      321          er+   257
  +lich    162
  +ten     160
```

The record lists the German endings and prefixes. An ending is a part that attaches to the end of a word. A prefix is a part that attaches to the front of a word. The record lists the endings and the prefixes in order of frequency. The frequency is the number of times that the ending or the prefix makes one part into a different part. The endings and the prefixes include `+en`, `+ung`, `+lich`, `+ten`, `be+`, `ge+`, `er+`.

The capital letters in the BEGINNINGS table (`A+`, `S+`, `E+`, `B+`) come from a rule of German: each noun starts with a capital letter. Thus the same stem occurs with a capital letter and without a capital letter.

```
CLASSES
  [+en, +t]
     52 members: beantrag, beleg, benoetig, beruecksichtig, beschraenk, besitz, betreib, beurteil, bewirk, bleib
  [+n, +r]
     42 members: einige, liebe, laendliche, gemeinschaftliche, nachhaltige, saemtliche, bestimmte, wenige, dritte
  [A+, a+]
     23 members: spekten, ussprache, nreize, uszahlung, nstrengungen
  [+n, +t]
     17 members: erwarte, aufforder, belaste, binde, entwickel, erarbeite, leiste
```

The class `[+en, +t]` has 52 members: beantrag, beleg, benoetig, beruecksichtig, beschraenk, and more. These members are stems that occur with `-en` and with `-t`. The 2 forms are the infinitive and the third-person form of a German verb. The class `[+n, +r]` has 42 members: einige, liebe, laendliche, nachhaltige, bestimmte. These members are adjectives. Adjectives accept the endings `-n` and `-r`.

The classes `[A+, a+]` and `[V+, v+]` contain the forms of the same stems with a capital letter and without a capital letter.

The record does not say "verb" or "adjective". The record says only this: 52 parts accept exactly the changes `+en` and `+t`, and 42 parts accept exactly the changes `+n` and `+r`.

## CRYSTAL

The CRYSTAL table is like a dictionary with 1 entry for each word. The program makes the entries from the signal alone.

```
  die   seen 862
    made of    di, ie, e, d
    part of    dieser, diese, diesem, dieses, dies, diejenigen, dienen, dieselbe
    changes    +ser, +se, +sem, +ses, +s, +jenigen, +nen, +selbe
    followed   Kommission 53, Mitgliedstaaten 19, Leitlinien 16, in 12, Regionen 11
    preceded   , 177, fuer 81, dass 60, auf 58, und 53, ueber 33

  Kommission   seen 125
    made of    ommission, Kommissio, Kommiss, Kommi, ssion, ion, K, n
    part of    Kommissionsdokument, EU-Kommission, Kommissionsd, Kommissions
    changes    +sdokument, EU-+, +sd, +s
    followed   , 17, ueber 6, in 5, und 5, im 4, das 3
    preceded   der 59, die 53, und 2, Europaeischen 2, neue 1
```

The entry for `die` lists dieser, diese, diesem, dieses as changes. These words are the different forms of the demonstrative (the German word for "this", "that", or "the"). The word `Kommission` comes after `der` 59 times and after `die` 53 times. The word `Kommission` is part of `Kommissionsdokument` and `EU-Kommission`.

## Level 1

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   160002        88    23206      4489    14721          405    19210       19210
      1    23206      4489     1703      1654    13315          404    14943       34153
      2     1703      1654        9         9        0            0        9       34162
      3        9         9        1         1        0            0        1       34163
```

The most common level-1 word is the comma. Thus a level-1 run is the sequence between 2 commas. The runs that occur most often are the forms of address:

- `Herr Kommissar`, 8 times
- `meine Damen und Herren`, 7 times
- `Frau Berichterstatterin`, 5 times
- `Frau Praesidentin`, 4 times

The ENDINGS table shows the words directly before a comma (`+der` 179, `+ist` 174, `+werden` 135). The BEGINNINGS table shows the words directly after a comma (`die+` 997, `der+` 642, `und+` 418). Level 2 has 9 runs and makes no new parts.

## The bridge: German to English

The script `bridge.py` runs the comparator between the 2 records and not inside 1 record. The comparator is the code of the program that compares 2 parts. A part that exists in both pools is a shared part. The parts that contain the shared part on each side are the differences.

```
BRIDGE   19210 parts in A, 10985 in B, 2188 shared

LONG SHARED PARTS
  international      A: internationalen                 B: internationally
  technologi         A: technologische, technologien    B: technologies, technological
  instrument         A: Arbeitsinstrument, instrumenten B: instruments
  transport          A: Gefahrguttransport, transportiert  B: transported, transportation
  programme          A: Kommissionsprogramme, sprogramme   B: programmes
  Wulf-Mathies       A: (whole)                         B: (whole)
```

There are 2,188 parts in both pools. The long shared parts are stems that the 2 languages share (international, technolog, transport, programm, instrument, operation) and proper names. A proper name is the same string on each side. Each shared part comes with its German parents and its English parents. The part `technologi` is inside `technologische` and `technologien` on the German side. The same part is inside `technologies` and `technological` on the English side.

The result is a bridge between 2 dictionaries. The program made the bridge from the parts that both signals contain and from no other source.

The shortest shared parts (`s`, `e`, `i`, `t`, `n`) have the highest density. These parts are the letters. These parts show only that the 2 files use the same alphabet.

## Summary of the record

From the German bits, the record shows:

- 8-bit words, with the top bit in use 3.6 percent of the time
- 1 byte that occurs only in front of 4 other bytes
- the letter order
- the words
- the endings `-en`, `-ung`, `-lich`, `-ten` and the prefixes `be-`, `ge-`, `er-`
- a class of 52 verb stems and a class of 42 adjective stems
- pairs of a stem with a capital letter and the same stem without a capital letter
- a dictionary entry for each word

From the 2 records together, the bridge shows 2,188 shared parts. The shared parts include the stems and the names that the 2 languages share. The shared parts also show the forms that each language makes on these stems.
