# Progress Notes

### 2019-12-07
Added new documentation and updated readme.

#### 2019-03-24
I've completely re-written most of Mahir. It now runs from inside a Jupyter notebook environment instead of from command line. This allows me to use Text-Fabric, and to see highlighted terms in context. I've vastly simplified the architecture, changing the code from module oriented to class oriented. `iMahir` now contains all of the principal code. A (mostly) arbitrary amount of scores can now be configured freely. However, there are some practical upper limits on division that prevents some possibilities, like a score 10 which would hardly ever appear in a study session. But the flexibility is at least now baked in. The biggest change, overall, is the mode of study: from lexeme-based gloss guessing to context-based. Now all terms are seen in their natural conjugated forms, highlighted in the middle of the verse that they appear in. This changes the learning experience, makes it more natural, and makes it easier to learn new terms. I have found that though it takes slightly longer to evaluate the conjugated surface form, my recall has increased since I am seeing words in context.


#### 2018-02-03
Added the ability to pull example passages from Text-Fabric, especially for use with the ETCBC BHSA dataset. The module will now load TF in advance. Examples are shown along with the surface form of the vocabulary term. The examples are selected at random from across the Hebrew Bible every time Mahir is loaded. For now, TF is loaded if it does not detect `"greek"` in the set's filename. This is a very primitive solution meant to prevent TF from loading with my Greek dataset. In the future, there should be a simple way of selecting which dataset to load, one which does not involve editing the config file everytime. Config data should instead go into the set data rather than being its own file. This would allow for the simple presence or absence of a text-fabric locations string to trigger whether TF is loaded or not. But for now, this low-level solution is sufficient for my purposes.

#### 2017-05-03
When scoring a new set of terms for the first time, it would probably be best to simply have two options: score 0 or 3.
I have encountered some issues with freely scoring 0-3, such as an unnaturally large number of score 1 or 2 cards, which results in deck sizes over the minimum.
This is an issue with the scorer module that I will fix in the near future.

Otherwise, I am using Mahir now with 3 languages: Hebrew, Greek, and Dutch. It is working well for vocabulary acquisition. However, I do notice
that it requires the user to think carefully about the scoring process. If a term goes into the score 3 set too early, it likely won't be seen for weeks in
a big set.

One idea to solve this problem: introduce a new quota for new score 3 terms. It will only pull from 50% (or so) from the new score 3 over the rest of the cycle.
Those terms will be selected at random. This way, new score 3 terms will still be encountered, but without clogging up too much of the term pipeline. I will have to see
how this goes in practice.

Also to do: add argparser to run Mahir with vocabulary file as a required argument instead of having to edit config file. Does Mahir really need a config file?
I would like to phase it out soon.
