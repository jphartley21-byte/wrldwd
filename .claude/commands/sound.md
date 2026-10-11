---
description: Build a sound set (the original's method) from a seed word: 8-16 different end words that chime, with jokes attached
argument-hint: <seed word or place, e.g. turkey> [--v ER,AO,IH --end IY]
---
Run `python toolkit/soundset.py $ARGUMENTS`. Read sections A-D. Choose 8-16 DIFFERENT end words (no repeats), prefer ones that carry a joke: a number (for a ladder), a drink/vice/place, a bank phrase ending (section C), an idiom tail. Pair each with a register idea from bank/register_stiff.csv and a trivial item/price from bank/mundane.csv, and note any idiom from bank/idiom_surgery.csv whose swap lands on it. Write the plan to `work/<section>/sound_<seed>.md` (end word | joke idea | register pair | idiom swap). Do not show Joe this; it feeds /chain.
