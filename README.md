# Mahir 0.6 Beta

Experimental, bulk, long-term vocabulary review program for command line.

© 2017 Cody Kingham, creative commons, CC BY-NC 4.0

## What is Mahir?

Mahir is designed for reviewing large amounts of vocabulary terms while still learning new ones. Vocabulary tools like Quizlet are good for small stacks of vocabulary words that are marked in a binary way (starred or unstarred, learned or unlearned). Mahir, on the other hand, specializes in **bulk** vocabulary review and learning with a focus on familiarity through a 0-3 ranking system. It is a management system that ensures a user sees familiar terms regularly (to stay familiar), while introducing new terms. As terms are scored by a user for familiarity, Mahir dynamically adjusts each study session to reflect the new scores. Familiar terms are seen at least once in a study cycle (group of sessions); less familiar terms are seen numerous times depending on their score.


## Running Mahir
`cd Mahir`

`python3 Mahir.py`

## Set-Up and Use

Input new terms by modifying config.json where:

	* "type" is "load," for .json files already config'ed by Mahir, or "new," for a directory containing a set of .tsv files with term and tab-seprated definitions.
	* "set" is either a directory location or the .json file already formatted by Mahir.
	* "delimiter" can be set to something other than "\t" if you want to load a directory csv files or other. *Note that in the beta version, the program only loads files with .tsv extensions*

For a new set, first run the scoring program by selecting "score" after start-up. Mark terms 0-3 based on familiarity (0 being unlearned and 3 being very familiar). Mahir will use your scores later for the study program to determine which and how many terms to populate a study session with. Those calculations are figured over a given study "cycle." A cycle is a user-selected number of sessions, over which period every term is seen at least once. Score 3 terms are seen once per cycle. Score 2 are seen 4x per cycle. Score 1 terms are seen 8x per cycle. And score 0 terms are seen each session until you mark them otherwise.

You may quit the scoring program and return when you want to finish. If you are running Mahir from a directory of .tsv files, you will be prompted to name your new set. The program will export a new .json file with the name you enter. Before continuing to resume scoring the set, or before attempting to run the study module after scoring is finished, be sure to exit Mahir, edit config.json (see "set") to "load" the newly generated json file, then restart Mahir. *(This is primitive, but will be fixed later.)* 

After all the terms are scored, you can run the "study" program to study your terms. You will be lead through a set-up process to set the minimum deck size and study cycle. During a study session, score terms 0-3. At the end of a full session, Mahir automatically accounts for the new scores for the cycle. The more terms you move to score 3 throughout the cycle, the more space is made during the cycle for new, score 0 terms.

Add new terms by running the "add" module within Mahir. You will need the file path to a csv file containing the terms, with a comma separated delimiter.

*This program has been built and tested on Mac OS 10.12.3 with Python 3.6. It has not yet been tested on other systems. I am sure some of the display features may be quirky in other terminals. Please let me know where you see room for improvement.*