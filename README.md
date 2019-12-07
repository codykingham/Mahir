# Mahir [![DOI](https://zenodo.org/badge/86166512.svg)](https://zenodo.org/badge/latestdoi/86166512)
>   עָלָה מִבָּבֶל וְהוּא־סֹפֵר מָהִיר בְּתוֹרַת משֶׁה

Corpus-driven vocabulary review program for use with [Text-Fabric](https://annotation.github.io/text-fabric/) and Jupyter notebook.

> <img src="docs/images/review_ex.png"><br>
> *Example of Mahir Study Session in the Hebrew Bible*

> <img width=75% height=50% src="docs/images/gloss_ex.png"><br>
> *Looking at the gloss-side of a term*

## What is Mahir?

Mahir is a **corpus-driven vocabulary review** program with an emphasis on **contextual learning of glosses**. The student of ancient corpora such as the Hebrew Bible or Greek New Testament is often faced with two sub-optimal choices when it comes to vocabulary acquisition. They may rely on traditional flash card systems (Anki, Quizlet, etc.), in which they must learn a word as a lexicalized form stripped of context. This technique of rote memorization is an unnatural way of learning language. It is difficult, slow, and ultimately not very helpful for idiomatic terms that strongly rely on context. The other option is to simply try to acquire vocabulary from rapid reading of text. While this is better from the standpoint of contextuality, it loses the benefit of systematically covering wide and diverse terms. It also makes the student a slave to the lexicon, which itself dulls the enjoyment of the reading process. This is especially problematic for highly poetic and abstract texts (e.g. Job in the Hebrew Bible). 

**The corpus-driven approach blends the contextuality of reading the text with the systematicity of flash-card review**. This is made possible by using [Text-Fabric](https://github.com/annotation/text-fabric). For any given term in a vocabulary set, Mahir randomly selects a verse/line where the term appears. The "front side" of the "card" is the plain-text of the verse with the term at hand highlighted. The user can then score the term based on familiarity. In difficult cases, the user may request a different context, which is again selected at random. 

### Review Strategy

The review strategy of Mahir is designed for reviewing large amounts of vocabulary terms while still learning new ones. This is currently achieved through a rudimentary ranking system and cycle period. The user sets a given number of sessions in which they want to cycle through all of their "common terms". Conversely, a "common term" is one which is seen once every set number of days. Currently, I have these common terms set as "score 3". For instance, if a cycle is set to 30 days, then score 3 terms will be seen once in that period. Score 2 terms are seen every 4 days in the period; score 1 every other day. Score 0 are terms that are seen every session until they are upgraded to 1. Finally, as I've acquired more and more terms, I've realized the need for super-cycle scores. So score 4 terms are seen every other cycle, score 5 every 2 cycles, score 6 every 4 cycles, and so on. 

**To-Do:** The rudimentary strategy outlined above is sub-optimal. Scores should be more automated, based on a spaced-repetition algorithm similar to Anki. One of the motivations of the current system is to keep the reviewer in full control. But maybe it is better to conceive of an automatic algorithm as a kind of autopilot. Allow intervention when desired. But otherwise, adjust terms in a way that is optimal for memorization. This issue requires further thought and work.

## Set-Up and Use

Your corpus will need to be in the [Text-Fabric corpus library](https://annotation.github.io/text-fabric/About/Corpora/). This requires 1) a corpus in TF format (instructions [here](https://annotation.github.io/text-fabric/Create/Convert/)), and 2) an app written to fit the corpus (instructions [here](https://annotation.github.io/text-fabric/Implementation/Apps/)). Finally, each of these elements need to be stored in a Github repository. The first should be in its own repo with a top-level directory called `tf`. The second must be stored under the `annotation/` organization's github. Please contact me for details. Of course, you may also simply rely on the numerous corpora already available in Text-Fabric.

You will also need a vocabulary .json file formatted in a way Mahir expects. See the [sample vocabulary json](sample_vocab/hebrew.json) to see how to do this.

Every term has a score, which tells Mahir how often it should be shown. Scores range from 0-4 but higher scores can be configured. The higher a score, the less often it is seen. For example, score 0 terms that fit in the daily quota are shown every session so they can be learned, score 1 terms are shown every other session. Score 3 terms are seen every cycle period. A cycle period is defined as an X number of sessions. Score 4 terms are super-cycle terms, they are only seen once every other cycle. These parameters can be tweaked in the `Session` object of `iMahir.py`.

## Running Mahir

From within a Jupyter notebook, invoke:

```
from iMahir import loadStudy

study = loadStudy('sample_vocab/hebrew.json')

study.learn()
```

The final call will invoke an interactive study session that shows terms in context.

## Progress Notes

See [here](docs/updates.md).

<hr>

© 2020 Cody Kingham, MIT License
