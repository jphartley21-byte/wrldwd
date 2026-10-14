# What makes a rap rhyme sound good: the evidence, and what the pipeline now enforces (13 Oct 2026)

Joe: "we probably need more theory research to figure out what actually makes rhymes sound good to the ear, so placement and vowel type are actually enforced
properly during the writing process." This is that research, kept honest about what each source does and does not show.

No lyrics of the original appear here (rule 4). Examples are the papers' or are synthetic.

## 1. Sources, and how much of each I actually read

| Source | What I read | Strength for "sounds good" |
|---|---|---|
| Hirjee & Brown 2009, *Automatic detection of internal and imperfect rhymes in rap lyrics*, ISMIR ([Zenodo](https://zenodo.org/records/1416160)) | full text (6 pp.) | method paper: how working rap rhyme is modelled; no listener test |
| Hirjee & Brown 2010, *Using automated rhyme detection to characterize rhyming style in rap music*, Empirical Musicology Review 5(4) ([DOI](https://doi.org/10.18061/1811/48548)) | abstract only | confirms the model; not read |
| Malmi et al., *DopeLearning* (arXiv [1505.04771](https://arxiv.org/pdf/1505.04771)) | full text (10 pp.) | corpus measure of rhyme length over 94 rappers; no listener test |
| Tait, Tabain & Sykes, stress and metrical position in American hip-hop (SST-14, [PDF](https://assta.org/proceedings/sst/SST-14/8.A.%20PROSODY/2.%20TAIT.pdf)) | full text (4 pp.) | measured rapping of 6 artists; where stress falls against the beat |
| Kawahara 2007, *Half rhymes in Japanese rap lyrics and knowledge of similarity*, J. East Asian Linguistics 16 | search abstract only | corpus: more similar consonants rhyme more often (m-n, t-s common; m-sh, n-p rare) |
| Katz 2015, *Hip-hop rhymes reiterate phonological typology*, Lingua 160 | secondary summary only (paywalled) | corpus of African-American English hip-hop: mismatches track perceptual similarity |
| Knoop, Blohm, Kraxenberger & Menninghaus 2021, *How perfect are imperfect rhymes?*, Psych. of Aesthetics, Creativity & the Arts 15(3) | abstract only | the only LISTENER experiment I found (German, speeded judgement) |
| Zwicky 1976, rock rhyme (CLS) | via Zwicky's own blog summary | argues rock rhyme is conventional "feature" and "subsequence" rhyme, not just perceptual similarity |
| Holtman 1996 (the similarity hierarchy Hirjee & Brown build on) | only as quoted by Hirjee & Brown | taxonomy of imperfect rhyme |

What was NOT found: a listener experiment on rap rhyme in English, and any study of rhyme carried only by unstressed syllables. Every claim below about
"sounds good" is therefore inferred from what skilled rappers DO, plus one German perception study, plus Joe's ear.

## 2. What the evidence says

**E1. The rhyme starts at the last stressed syllable.** Hirjee & Brown define the rhyme of a line pair as "all syllables following the final primary-stressed
syllable" (after Holtman), start a rhyme only from an anchor that contains a stressed syllable or is line-final, and then **filter out one-syllable rhymes that include
unstressed syllables because they "tended to be noise"**. A match that lives only in an unstressed tail ("-it" of biscuit / credit) is not what the field counts as a rhyme.

**E2. Stress lands on the strong beat, and rappers bend words to make it.** In six American hip-hop artists primary-stress syllables sit mostly on strong metrical
positions (34.6% of them in position 2, average metrical strength 2.18) while unstressed syllables pile into the weakest position (average strength 3.57; 55% of all
unstressable syllables in the weakest slot). About 11% of words in the closely analysed artist showed a stress shift, mostly so a stressed syllable could reach a
strong position. So a rhyme on an unstressed syllable falls on a weak beat and is not heard as the rhyme; a performer would have to bend the word to rescue it.

**E3. Assonance is the working rhyme of modern rap; consonants are free to vary within limits.** DopeLearning: the assonance rhyme is "the most common rhyme type
nowadays, due to its versatility"; multisyllabic rhyme is a matching VOWEL sequence that can span several words; rhyme density (average length of the longest matching
vowel sequence per word) runs from about 0.87 to 1.19 across 94 rappers (top: 1.19; Eminem 1.05, held down because he "bends" words, which a vowel detector cannot see).
So multisyllabic matching is a SELECTIVE device, not something every word does.

**E4. The mismatch that is allowed is the small one.** Hirjee & Brown: a normal rhyme shares nucleus and coda; an imperfect rhyme breaks one of them, but not at random
("there is a constraint to the amount of dissimilarity"). Holtman's hierarchy, which their learned matrices largely reproduce: most similar consonants = nasals,
fricatives, and plosives that differ only in place (m/n); less similar = same place, differing voicing or continuancy (k/g); vowels are most similar when they differ
only in height or length. Kawahara (Japanese) and Katz (American English) find the same shape: rhyme mismatches follow perceptual similarity.

**E5. Longer rhymes are mosaic, span words, and can have gaps.** Hirjee & Brown describe triplet-or-longer rhymes whose unstressed syllables follow an initial stressed
pair, spanning several words, with more than one stressed pair possible, and allow a "jump" of one or two non-rhyming syllables inside a longer rhyme. Internal rhymes come
as chain (consecutive words each rhyming with the last), compound (two overlapping pairs inside a line) and bridge/link rhymes (across lines).

**E6. Context makes an imperfect rhyme acceptable.** Knoop et al. 2021 (German, speeded judgement): imperfect rhymes were judged less acceptable than perfect ones and
produced MORE uncertainty than either perfect rhymes or non-rhymes; a metered verse context raised acceptability; degree of phonological similarity was central. Read:
an imperfect rhyme is safest inside an established carpet and on the beat.

**E7. Contrary view.** Zwicky (1976) argues rock rhyme cannot be derived from segment similarity alone; it relies on conventional feature and subsequence rhyme. Taste
and convention matter, which is a reason to calibrate against the original and to keep Joe's ear in the loop rather than trust any score.

## 3. What this means for "placement" and "vowel type"

PLACEMENT (where the rhyme sits)
- The rhyme-bearing syllable is the last stressed one, or a long vowel/diphthong that closes the bar (Tobago / luego on the final -o). It must fall on a strong beat.
- Every bar in a rhyme group should put that syllable in the same place: same end shape (|S, |Sw, |Sww). Mixed shapes cost a beat.
- A short unstressed vowel is never the rhyme (it, -er, -ing, -a): at most it is the tail of a rhyme whose stressed syllable already matches.

VOWEL TYPE (what must match)
- The STRESSED vowel is the load-bearing part. Identical, or differing only in height or length (Holtman), or a diphthong sharing a glide. Different vowels with a matching
  tail are an echo, not a rhyme.
- Coda consonants may differ, ranked by similarity (m/n, p/t/k place changes, then voicing). Assonance alone is legitimate at a stressed position (goose / cruise / suit).
- Long vowels and diphthongs keep their weight even when unstressed (bonjour-NO), short ones do not.

## 4. Rules, where they are enforced, and their status

| # | Rule | Basis | Where | Status |
|---|---|---|---|---|
| R1 | A rhyme pair must match through a stressed or long-vowel syllable. A bar whose only partners share an unstressed tail ("-it") fails. | E1, E2 | `slotcheck.check` -> `rapfit.check_block` (HARD) | ENFORCED 13 Oct. Switch: `WW_RAPFIT_GATE=0`. |
| R2 | Stressed vowels in a group match (identity, height/length, or shared glide). | E4 | inside R1 (`rapfit.chain`) | ENFORCED via R1 |
| R3 | Rhyme depth for a slot is at least the original's (1 stressed syllable in Hook 1-4, V1 9-16, V2 1-8; 2 in Hook 5-8, V1 1-8, V1 25-32; 3 in V1 17-24). | E3, E5 and the original | `benchmark/rhyme_depth_targets.json`, reported SOFT | reported, not yet a gate |
| R4 | End-word menus offer only words that rhyme with the family anchor through a stressed syllable. | E1, E4 | `draft_all.end_menu` filter | ENFORCED (falls back if it would empty the menu) |
| R5 | The writer is told what rhyme means: stressed syllable + everything after it; a shared unstressed ending is not a rhyme. | E1 | `block_writer.SYSTEM` | ENFORCED (prompt) |
| R6 | Same end shape across a group; the rhyme lands on the bar's last strong beat. | E2 | existing end-shape gate | already enforced; landing-step equality still proposed |
| R7 | Imperfect rhymes sit inside an established carpet, not alone. | E6 | existing carpet gate | already enforced |
| R8 | Multi-syllable internal chains (2+ DISTINCT vowels, e.g. iː-aʊ repeated) are a quality device; a single vowel piled up is not. | E3, E5 + Joe's ear | `rhymeview` chains | DIAGNOSTIC ONLY: at chance level so far, see below |

## 5. Known gaps

- The chain detector finds the iː-aʊ pattern Joe pointed to, but across a whole song the number of chains it finds is about what shuffled vowels give by chance in the
  original, draft 8 and draft 9 alike. It cannot yet tell craft from coincidence, so it must not rank anything until it is made stricter (coda agreement, rarity-weighting).
- "Stressed" comes from a dictionary. Rap stress is conditioned by the beat (Tait; Adams on flow), and bent words (E3) are invisible. British speech differs from the American
  data the papers use (DopeLearning used American eSpeak; Tait's artists are American): the original's moi / dance and Jamaica / Mainz links are exactly where the tool is blind.
- The floor (0.50) and the depth targets are fitted on Joe's by-ear scheme for the original. No pair in the repo is labelled "technically rhymes but sounds flat", so R1's
  cap is argued from E1/E2, not fitted. `writing/rhyme_ear_labels.md` is the sheet that would fit it.
