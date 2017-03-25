from glob import glob
import csv, json

def loadNewSet(dir_name, delimiter='\t'):
    '''
    Load and format a .csv or .tsv vocabulary set.
    '''

    # store formatted terms here
    terms = {}
    # unique ID for terms, incremented in loop
    cur_id = 0

    # find all the decks
    decks = tuple(file for file in glob(f'{dir_name}*.tsv'))

    # add decks' cards to terms dict
    for deck in decks:
        with open(deck) as deck_file:
            reader = csv.reader(deck_file, delimiter=delimiter)

            # assign id and add to dict
            for term in reader:
                cur_id += 1
                terms[cur_id] = {'term': term[0],
                                 'definition': term[1]}

    return terms

def loadExistingSet(file_name):
    '''
    Load an existing .json vocabulary set.
    '''
    with open(file_name) as setfile:
        terms = json.load(setfile)

    return terms