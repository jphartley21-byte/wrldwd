# Suno rap rules sheet (researched 7 Oct 2026)
Tags: [O] official Suno, [C] third-party (rule of thumb), [M] inference.

## 0. Flags
- **V5.5 is retired.** [O] "All models prior to v6 have been retired" (9 Sep 2026): v6, v6-wild (Pro/Premier), v6-mini (free). Old songs stay; extending/covering them runs on v6, so the voice may drift. Re-test V5.5 prompts.
- **200 characters is obsolete** (V4 and older). Since V4.5, unchanged in v5.5/v6, web UI: Style 1,000, Lyrics 5,000, Exclude 1,000 [C, read from the composer], Title 80-100. API: Exclude 200, Title 80.
- **Short still wins.** 4-8 non-conflicting descriptors (~150-350 chars). Lyrics past ~3,000 chars / ~60 lines get rushed or skipped. [C]
- **Names.** Joe, 14 Oct 2026 (from using Suno): artist and celebrity names are FINE in the LYRICS box; only the STYLE (and exclude) field is moderated. So name real artists, films, brands and places freely in lyrics for texture; keep artist names, 'sounds like' and song titles ("Pete & Bas", "Mr Worldwide") OUT of the style prompt and the title. (Earlier note, superseded: a third-party rule of thumb said lyrics are checked too.)

## 1. Controls (Custom > Advanced)
- Vocal Gender Male: a guide, not a guarantee; also write "gruff" in style. [O]
- Weirdness (Safe-Chaos, 50% normal [O]): start ~30. [M; sources say 20-50]
- Style Influence (Loose-Strong, default ~50% [C]): 65-75 for a precise prompt.
- Variety (v6): 0, else Suno rewrites your style prompt. Max Mode (costs more): finals over 2 min. [O]
- Exclude: short noun list, "a request, not proof". Negatives typed in the Style box act as inclusions. [O/C]

## 2. Style recipe
Order: genre, vocal, delivery/accent, tempo, drums, bass, melody, mix. Max two genres; no contradictions (shouted vs laid-back vs monotone: use "barked, flat intonation").
Style (180 chars): `UK drill, rapped male vocal, gruff barked flat deadpan delivery, south england accent, 140 BPM half-time, sliding 808s, triplet hi-hats, sparse minor-key piano, dry close-mic vocal`
Exclude: `singing, melodic hook, autotune, choir, female vocals`
LESS GENERIC, CLOSER TO THE ORIGINAL (17 Oct 2026, Joe: "make the song less generic drill"): the original's beat is a bright Latin party riff (WhoSampled: "Voodoo Song", the riff "Mi Gente" reworks) retimed under drill drums, in a major key (songbpm: D major), riff from the first bar. Describe that, never name it (no artist or song titles in Style):
Style: `UK drill flipped with a Latin moombahton party riff, rapped male vocal, gruff raspy London voice, flat deadpan cocky delivery, 140 BPM half-time, bouncy syncopated drill drums, triplet hi-hat rolls, sliding 808 bass, bright catchy pitched vocal-chop lead riff looping from the first bar, nasal kazoo-like hook melody, sunny playful tropical feel, dry close-mic vocal, clear diction`
Exclude: `singing, sung chorus, autotune, choir, female vocals, dark piano, eerie strings, horror bells` ("melodic hook" dropped: it fights the riff; "sung chorus" keeps the hook rapped)
BPM is approximate; above 145 drifts to EDM; also test "70 BPM". "Anthemic/crowd/arena" summons choirs. [C]

## 3. Lyrics box
- Bracket tag on its own line with a short cue; v6 reads cues [C]: `[Verse 1: rapped, gruff, flat deadpan]`, `[Hook: call and response, gang vocals]`, `[Intro: 2 bars, drums only]` (bare intros run 30-60 s).
- Line break = breath, blank line = vocals stop, comma = short pause, period = reset, hyphen stretches (invites singing). [C]
- One line per half-time bar (~3.4 s at 140 BPM) [M]: 8-12 syllables, neighbours within 2; beyond ~13 rushes or mumbles. Verses 8-12 lines (16 gets machine-gunned), hook 2-4 lines played max 3 times, ~2:30-3:00 total. [C]
- Ad-libs/backing in parentheses, 1-2 per section (v6 still turns them into backing voices); identical wording for each call and response. [C]
- Anti-singing: "rapped vocal, spoken flow, rhythmic delivery", `[Rap]` per section, Exclude above. Anti-mumble: "clear diction, crisp consonants", no lo-fi/hazy tags, short words, 3-5 takes. [C]
- Slang: spell plainly; respell only failures, by sound (IPA unsupported). The accent phrase in style beats respelling everything. [C]

## 4. Fixing
- Take-to-take variance can exceed a prompt change [C]: change one variable per round; judge at least two Creates. Lyrics first, style second.
- Weak line/verse: Replace Section (Pro/Premier): highlight whole lines, new lyrics, two candidates, returns a full song. [O] Smaller is safer; compare against the keeper. v6 Edit swaps a word/line, voice may drift. [C]
- Weak ending: Extend, then "Get Whole Song". Cover keeps melody, changes style. Remaster polishes clarity, not lyrics. A Persona from the best take anchors the voice (check v6 compatibility). [O]

## 5. Rap craft
- Four stresses a bar; stressed rhyme syllable on beat 4/snare.
- Monorhyme: hold one vowel shape 4-8 bars, swap unstressed filler each bar, change vowel every 8-16, break with an AXAA non-rhyming line to set up a punchline.
- Multis: 2-3 syllables, matching stress, rhyme by mouth shape not spelling, mix perfect and slant, internal rhymes between kick and snare, enjambment across the bar line, move rhymes between beats 3 and 4 to dodge sing-song.
- Punchline: set up early, rhyme word is the turn, reveal on the last stressed word, understate, call back later; never signal or explain. Pete & Bas comedy is straight-faced incongruity. [C]
- Specific beats generic: person, place, object, action, consequence.

## 6. AI tells to cut
- Words: neon, echoes, whispers, shadows, embers, tapestry, rise, soar, chains/wings, concrete jungle, king/throne, grind/hustle, we/our.
- Shapes: tidy AABB quatrains/couplets (GPT poems: quatrains 60-70% vs 17% human; end rhyme 90% vs 65%), equal-length lines, no syncopation, no internal rhyme, "not X but Y", rule of three, back-to-back repeated words, abstract nouns/emotion labels without action, constant peak emotion, redemptive moral last verse, hook that just repeats the title, rhyme choosing the content (write the punchline first, build the rhyme backward). Authentic rap shows varied vocabulary and dense rhyme.

## 7. Beat words
- UK drill: 140-144 BPM, half-time (snare on beat 3, feels like 70), sliding 808s, hats straight 16ths then triplet runs, syncopated kick, 2-3 note minor piano/strings/bells, sparse, cold.
- Grime: ~140, snare/clap on 2 and 4, raw square-wave bass stab, minimal hats, "eski click".
- UK garage: 130-138, 2-step kick, late swung hats, chopped vocals.

## Sources
https://help.suno.com/en/articles/13924481
https://help.suno.com/en/articles/6141377
https://help.suno.com/en/articles/3161921
https://help.suno.com/en/articles/3198209
https://help.suno.com/en/articles/10153473
https://help.suno.com/en/articles/3271873
https://help.suno.com/en/articles/2409601
https://help.suno.com/en/articles/8105281
https://help.suno.com/en/articles/3484161
https://hookgenius.app/learn/suno-character-limits/
https://aimusicapi.ai/en/blog/suno-ai-prompt-character-limits
https://hookgenius.app/learn/suno-v6-guide/
https://heho.ai/blog/suno-v6-what-changed-for-lyrics
https://hookgenius.app/learn/suno-hip-hop-prompts/
https://songsmith.studio/blog/suno-punctuation-is-rhythm
https://hookgenius.app/learn/fix-suno-rushed-lyrics/
https://hookgenius.app/learn/fix-suno-mumbling/
https://github.com/xfactor21/claude-suno-skils/blob/main/reference/suno/pronunciation-guide.md
https://rhymeflux.com/blog/rap-rhyme-schemes-explained/
https://rhymeflux.com/blog/how-to-write-multisyllabic-rhymes/
https://rhymeflux.com/blog/how-to-count-rap-syllables/
https://www.mtosmt.org/issues/mto.09.15.5/mto.09.15.5.adams.html
https://arxiv.org/html/2410.15299v1
https://pmc.ncbi.nlm.nih.gov/articles/PMC6804983/
https://jackrighteous.com/en-us/blogs/music-creation-process-guide/avoiding-ai-cliches-in-lyrics-keep-your-songwriting-fresh-and-original
https://www.tracklib.com/blog/drill-beat
https://orphiq.com/resources/what-is-grime-music
https://orphiq.com/resources/what-is-uk-garage
https://www.rapreviews.com/2021/06/pete-bas-quick-little-mixtape
