# Breakdown: German from the raw bytes

## The input

The file `ep-00-01-17.de` is one day of debate in the European Parliament (17 January 2000) in German, 160,002 bytes. The file `ep-00-01-17.en` is the same day in English. The German file is stored as UTF-8, a way of writing text as bytes in which the letters a-umlaut, o-umlaut, u-umlaut, and sharp-s each take 2 bytes instead of 1.

```
python discovery.py examples/german/ep-00-01-17.de --lens utf8
python discovery.py examples/german/ep-00-01-17.en --lens ascii
python bridge.py ep-00-01-17.de.record.json ep-00-01-17.en.record.json
```

The `--lens utf8` option is a display setting. It makes the record print a whole run as readable text, so an a-umlaut shows up as the letter and not as two hexadecimal codes. In the WORDS table, which lists single bytes, the lens shows the bytes one at a time, so there the 2-byte letters appear as pairs of bytes. The lens changes only how the output looks.

## FRAME: 8-bit units, with the top bit used 3.6 percent of the time

The program first works out how wide one unit of the file is. It tries many widths. For each width, it lays the bits out in rows of that width and measures how often each column is 1. The width where the columns differ the most wins. This is the FRAME table, and the lines below are its rows for the winning width.

```
    8    0.892   col   0 at 0.036   col   2 at 0.928
  chosen width 8
  column rates at width 8:
    0.036 0.803 0.928 0.245 0.315 0.494 0.377 0.462
```

The answer is the same as for the English novel: 8 bits, one byte. But this time column 0 is not 0. The top bit of each byte is 1 in 3.6 percent of the units. In Alice, column 0 was 0.000. That one number is enough to tell this file apart from a file that uses only 7 bits.

## WORDS: 88 different words, including `\xc3`

Next the program cuts the file into 8-bit units and counts how many times each different unit appears. The record calls these units words. Here a word is one byte, not a German word. This is the WORDS table.

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

The words with the top bit set are the bytes of the 2-byte UTF-8 letters. The word `11000011` (`\xc3`) is the first byte of a-umlaut, o-umlaut, u-umlaut, and sharp-s, and it occurs 2,827 times. The FOLLOWS table, which counts how often each word comes right after each other word, shows that this byte is always followed by one of 4 bytes. Those 4 bytes are the 4 special letters.

The record doesn't know what UTF-8 is. All it shows is a byte that only ever appears right before 4 other bytes.

The letter order is e, n, i, r, t, s, d, a, h, u. In Alice it was e, t, a, o, h, n. The two languages have two different frequency orders, and the program ran the same steps on both.

## RUNS: the German words

The program takes the most common word as the divider, which the record calls the separator. Here that is the space, so it cuts the file at every space. Each stretch between two spaces is a run, and the runs are the German words. This is the RUNS table.

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

The comma is a run on its own here because this text puts a space on each side of every comma. The RUN FOLLOWS table counts which run comes after which. The most common pairs are:

- `, dass`, 244 times
- `, die`, 177 times
- `fuer die`, 81 times
- `in den`, 68 times
- `der Kommission`, 59 times
- `die Kommission`, 53 times
- `moechte ich`, 45 times
- `.\nHerr Praesident`, 42 times

## ENDINGS, BEGINNINGS, and CLASSES

After cutting the runs, the program compares them with each other. When two runs share a start, it splits them into the shared start and the two leftovers, and each piece becomes a part. It does the same for shared ends. This is the mint step, and it keeps going, comparing the new parts too, until a round finds nothing new. The leftover after a shared start is an ending: something that attaches to the end of a part to make another part. The leftover before a shared end is a beginning: something that attaches to the front. The program counts how many times each ending and each beginning turned one part into another, and lists them in that order.

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

The record lists the German endings and prefixes in order of how often each one turned one part into a different part. They include `+en`, `+ung`, `+lich`, `+ten`, `be+`, `ge+`, `er+`.

The capital letters in the BEGINNINGS table (`A+`, `S+`, `E+`, `B+`) come from a rule of German: every noun starts with a capital letter. So the same stem appears both with a capital and without one.

A change is what you add to one part to make another part, so `+en` is a change. A class is a group of parts that all take exactly the same set of changes. The CLASSES table lists these groups.

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

The class `[+en, +t]` has 52 members: beantrag, beleg, benoetig, beruecksichtig, beschraenk, and more. These are stems that appear with `-en` and with `-t`, which are the infinitive and the third-person form of a German verb. The class `[+n, +r]` has 42 members: einige, liebe, laendliche, nachhaltige, bestimmte. These are adjectives, which take the endings `-n` and `-r`. You can check both against any German grammar.

The classes `[A+, a+]` and `[V+, v+]` hold the capitalized and uncapitalized forms of the same stems.

The record never says "verb" or "adjective". It says only this: 52 parts take exactly the changes `+en` and `+t`, and 42 parts take exactly the changes `+n` and `+r`.

## CRYSTAL

The CRYSTAL table gathers everything the record knows about one run into a single entry, one entry for each common run. Each entry lists the smaller parts the run is made of, the larger parts it is part of, the changes that turn it into those larger parts, what tends to follow it, and what tends to come before it. It reads like a dictionary entry, but the program builds it from the file alone.

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

The entry for `die` lists dieser, diese, diesem, dieses among its changes. These are the different forms of the demonstrative, the German word for "this", "that", or "the". The entry for `Kommission` shows that it comes after `der` 59 times and after `die` 53 times, and that it is part of `Kommissionsdokument` and `EU-Kommission`.

## Level 1

When the first level is done, the program treats each run as a single unit and does everything again one level up: it finds the most common run, uses it as the new separator, cuts the file at it, compares the new runs, and adds what it finds to the same pool of parts. The LEVELS table summarizes each level in one row: how many units it started with and how many were different, how many runs it cut and how many were different, how many parts the mint step made, how many classes with two or more members it found, how many parts it added, and the running total of the pool.

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   160002        88    23206      4489    14721          405    19210       19210
      1    23206      4489     1703      1654    13315          404    14943       34153
      2     1703      1654        9         9        0            0        9       34162
      3        9         9        1         1        0            0        1       34163
```

The most common level-1 unit is the comma, so a level-1 run is everything between two commas. The runs that occur most often are forms of address:

- `Herr Kommissar`, 8 times
- `meine Damen und Herren`, 7 times
- `Frau Berichterstatterin`, 5 times
- `Frau Praesidentin`, 4 times

The level-1 ENDINGS table shows the words that come right before a comma (`+der` 179, `+ist` 174, `+werden` 135). The BEGINNINGS table shows the words that come right after one (`die+` 997, `der+` 642, `und+` 418). Level 2 has 9 runs and makes no new parts.

## The bridge: German to English

The script `bridge.py` takes the two records, one for each language, and runs the program's comparison between them instead of inside one of them. The comparison is the same piece of code that compares two parts and finds what they share. A part that exists in both pools, the German one and the English one, is a shared part. The larger parts that contain the shared part on each side are where the two languages differ.

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

There are 2,188 parts in both pools. The long shared parts are stems the two languages have in common (international, technolog, transport, programm, instrument, operation) and proper names, which are the same string on both sides. Each shared part comes with the German parts that contain it and the English parts that contain it. The part `technologi` sits inside `technologische` and `technologien` on the German side, and inside `technologies` and `technological` on the English side.

The result is a bridge between two dictionaries. The program built it from the parts that both files contain, and from nothing else.

The shortest shared parts (`s`, `e`, `i`, `t`, `n`) have the highest density, meaning the most other parts containing them. They are single letters, and they show only that the two files use the same alphabet.

## Summary of the record

From the German bytes, the record shows:

- 8-bit units, with the top bit used 3.6 percent of the time
- 1 byte that appears only in front of 4 other bytes
- the letter order
- the words
- the endings `-en`, `-ung`, `-lich`, `-ten` and the prefixes `be-`, `ge-`, `er-`
- a class of 52 verb stems and a class of 42 adjective stems
- pairs of a stem with a capital letter and the same stem without one
- a dictionary entry for each word

From the two records together, the bridge shows 2,188 shared parts. They include the stems and the names that the two languages share, and they also show the forms that each language builds on those stems.
