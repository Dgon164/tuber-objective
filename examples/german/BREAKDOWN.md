# Breakdown: learning German from the signal

## What goes in

`ep-00-01-17.de` is one day of European Parliament proceedings (17 January 2000) in German, 160,002 bytes. `ep-00-01-17.en` is the same day in English. The German file is UTF-8, which means letters like ä, ö, ü and ß each take two bytes instead of one.

```
python discovery.py examples/german/ep-00-01-17.de --lens utf8
python discovery.py examples/german/ep-00-01-17.en --lens ascii
python bridge.py ep-00-01-17.de.record.json ep-00-01-17.en.record.json
```

The `utf8` lens shows whole runs as readable text, so `ä` shows up as `ä` instead of two hex codes. In the WORDS table, single bytes are still shown one at a time, which is where the two-byte letters appear as pairs.

## Frame: 8-bit words, and the top bit is used 3.6% of the time

```
    8    0.892   col   0 at 0.036   col   2 at 0.928
  chosen width 8
  column rates at width 8:
    0.036 0.803 0.928 0.245 0.315 0.494 0.377 0.462
```

Same answer as the English text — 8 bits. But column 0 is not zero this time: 3.6% of the words have the top bit turned on. In Alice it was 0.000. That one number already tells this file apart from a pure 7-bit one.

## Words: 88 of them, including `\xc3`

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

The top-bit words are the UTF-8 pieces. `11000011` (`\xc3`) is the first byte of ä, ö, ü, and ß. It appears 2,827 times. The FOLLOWS table shows it is always followed by one of four specific bytes — the four letters. Nothing in the record knows what UTF-8 is. It just shows a byte that only ever appears right before four other bytes.

The letter order is e, n, i, r, t, s, d, a, h, u. In Alice it was e, t, a, o, h, n. Two languages, two different frequency orders, same process.

## Runs: the German words

```
RUNS   23206 runs between separators, 4489 distinct
  ,             1702
  der            878
  die            862
  und            629
  in             376
  den            302
  zu             271
  daß            263
  für            248
  Kommission     125
```

The comma is a run on its own here because the text puts a space on both sides of it. RUN FOLLOWS shows pairs: `, daß` 244 times, `, die` 177, `für die` 81, `in den` 68, `der Kommission` 59, `die Kommission` 53, `möchte ich` 45, `.\nHerr Präsident` 42.

## Endings, beginnings, and classes

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

The record lists the German endings and prefixes by how often they turn one part into another: `+en`, `+ung`, `+lich`, `+ten`, `be+`, `ge+`, `er+`. The capital letters showing up as beginnings (`A+`, `S+`, `E+`, `B+`) come from German capitalizing nouns — the same stem appears both capitalized and not.

```
CLASSES
  [+en, +t]
     52 members: beantrag, beleg, benötig, berücksichtig, beschränk, besitz, betreib, beurteil, bewirk, bleib
  [+n, +r]
     42 members: einige, liebe, ländliche, gemeinschaftliche, nachhaltige, sämtliche, bestimmte, wenige, dritte
  [A+, a+]
     23 members: spekten, ussprache, nreize, uszahlung, nstrengungen
  [+n, +t]
     17 members: erwarte, aufforder, belaste, binde, entwickel, erarbeite, leiste
```

The class `[+en, +t]` has 52 members: beantrag, beleg, benötig, berücksichtig, beschränk, and so on. These are stems that appear both with `-en` and with `-t` — the infinitive and the third-person form of a German verb. The class `[+n, +r]` has 42 members: einige, liebe, ländliche, nachhaltige, bestimmte — adjectives, which take `-n` and `-r` endings. The classes `[A+, a+]` and `[V+, v+]` are the capitalized and uncapitalized forms of the same stems.

The record does not say "verb" or "adjective." It says: here are 52 parts that take exactly these two changes, and here are 42 that take exactly those two.

## Crystal

```
  die   seen 862
    made of    di, ie, e, d
    part of    dieser, diese, diesem, dieses, dies, diejenigen, dienen, dieselbe
    changes    +ser, +se, +sem, +ses, +s, +jenigen, +nen, +selbe
    followed   Kommission 53, Mitgliedstaaten 19, Leitlinien 16, in 12, Regionen 11
    preceded   , 177, für 81, daß 60, auf 58, und 53, über 33

  Kommission   seen 125
    made of    ommission, Kommissio, Kommiss, Kommi, ssion, ion, K, n
    part of    Kommissionsdokument, EU-Kommission, Kommissionsd, Kommissions
    changes    +sdokument, EU-+, +sd, +s
    followed   , 17, über 6, in 5, und 5, im 4, das 3
    preceded   der 59, die 53, und 2, Europäischen 2, neue 1
```

`die` → dieser, diese, diesem, dieses: the forms of the demonstrative, listed as changes. `Kommission` is preceded by `der` 59 times and `die` 53 times, and is part of `Kommissionsdokument` and `EU-Kommission`.

## Level 1

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   160002        88    23206      4489    14721          405    19210       19210
      1    23206      4489     1703      1654    13315          404    14943       34153
      2     1703      1654        9         9        0            0        9       34162
      3        9         9        1         1        0            0        1       34163
```

The most common level-1 word is the comma, so a level-1 run is a stretch between commas. The most repeated stretches are the forms of address: `Herr Kommissar` 8 times, `meine Damen und Herren` 7, `Frau Berichterstatterin` 5, `Frau Präsidentin` 4. The ENDINGS show what comes right before a comma (`+der` 179, `+ist` 174, `+werden` 135) and the BEGINNINGS show what comes right after one (`die+` 997, `der+` 642, `und+` 418). Level 2 has nine runs and produces nothing new.

## The bridge: German to English

`bridge.py` runs the comparator between the two records instead of inside one. A part that exists in both pools is the same; its containing parts on each side are the different.

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

2,188 parts appear in both pools. The long ones are stems the two languages share (international, technolog, transport, programm, instrument, operation) and proper names, which are the same string on both sides. Each shared part comes with its German parents and its English parents: `technologi` is inside `technologische` and `technologien` on one side and `technologies` and `technological` on the other. That is a bridge between two dictionaries, built from nothing but the parts both signals contain.

The shortest shared parts (`s`, `e`, `i`, `t`, `n`) have the highest density — they are the letters, and they only tell you that both files use the same alphabet.

## What this adds up to

From the German bits: 8-bit words with the top bit in use 3.6% of the time. A byte that only ever appears in front of four other bytes. The letter order. The words. The endings `-en`, `-ung`, `-lich`, `-ten` and the prefixes `be-`, `ge-`, `er-`. A class of 52 verb stems and a class of 42 adjective stems. Capitalized/uncapitalized pairs. And a dictionary entry per word. From the two records together: 2,188 shared parts, with the stems and names the two languages have in common and the forms each language builds on them.
