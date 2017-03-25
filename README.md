# Mahir 0.5 Beta,
Experimental, long-term learning vocabulary program for command line.
© 2017 Cody Kingham, creative commons, CC BY-NC 4.0

Python 3.6


`python3 Mahir.py`


Input new terms by modifying config.txt where:
	* "type" is "load" or "new", depending on whether you are loading a directory of tsv files (term \t definition) or loading a .json already formatted by Mahir. 
	* "set" is either a directory location or the .json file already formatted by Mahir.
	* "delimiter" can be set to something other than "\t" if you want to load a directory csv files or other. 


For new terms, first run the scoring program by selecting "score" after start-up. You may quit the scoring program and return when you want to finish.

After all the terms are scored, you can run the "study" program to study your terms. Mark terms 1-3 based on familiarity. You will be lead through a set-up process to set the minimum deck size and the study cycle. A study cycle is a number of sessions you want to make. During a study cycle, you will see all your cards at least once. Score 3 cards are seen once per cycle. Score 2 are seen 4x per cycle. Score 1 cards are seen 8x per cycle. And score 0 cards are seen each session until you mark them otherwise.

Mahir automatically accounts for the new scores during a review period. 

*This program has been built and tested on Mac OS 10.12.3 with Python 3.6. It has not yet been tested on other systems.*