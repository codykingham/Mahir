import collections, math, random, time, copy
from Ui import clearDisplay, askQuestion, displayNew
from datetime import datetime

'''
ManageSets.py contains functions relating to the creation and management of study sets and their decks.
A study set is all of the terms within a program.
A deck is the unique arrangement of terms seen during a study session.
'''

def createTermQueues(terms_dict):
    '''
    Returns dict of term ID lists corresponding to their score.
    The keys are the score strings (e.g. "3")
    The values are lists containing:
        the ID numbers of a term in terms_dict (e.g. "44")
    '''

    # gather all the terms
    term_queues = collections.defaultdict(list)

    for term, term_data in terms_dict.items():
        score = term_data['score']
        term_queues[score].append(term)

    # randomize the term orders
    for score, terms in term_queues.items():
        random.shuffle(terms)

    return term_queues


def buildDeck(term_queues, s3_seen, deck_min=100, cycle_len=60):
    '''
    Constructs a deck for a session that contains words scored 0-3.
    term_queues is a dict with scores as keys, lists as values containing term IDs.
    s3_seen are integer count of S3 terms newly marked as S3 during a cycle.
    deck_max defines when S0 (new) cards should be inserted into a deck. (deck_max - deck_min = available_space).
    cycle_len is the number of days in a full review cycle that buildDeck should calculate.

    The key to buildDeck is the term queue.
    The term queue is a list of term IDs of a given score.
    These lists are modified while a deck is constructed.
    When buildDeck adds terms to a deck, it also moves them to the end of their queue (with list.pop(0)).
    The modified lists are then returned (along with the deck) to be used for the next study session.
    The cycle is repeated in the subsequent session.

    buildDeck pulls from lesser-known terms more often, which means their words cycle back more often.
    S3 terms appear once per cycle.
    S2 terms appear every 4 review sessions.
    S1 terms appear ever other review session.
    S0 terms appear indefinitely (until they are marked otherwise).
    '''

    s_counts = dict((score, len(terms)) for score, terms in term_queues.items())

    # calculate daily deck quota
    s3_quota = math.ceil((s_counts['3'] - s3_seen) / cycle_len) if '3' in s_counts else 0  # math.ceil rounds up
    s2_quota = math.ceil(s_counts['2'] / 4) if '2' in s_counts else 0 # term is seen every 4 sessions
    s1_quota = math.ceil(s_counts['1'] / 2) if '1' in s_counts else 0 # term is seen ever other session

    # construct a study deck and keep stats
    deck = []
    deck_stats = collections.Counter()

    # add quotas from scores 1-3
    for score, quota in (('1', s1_quota), ('2', s2_quota), ('3', s3_quota)):
        while quota > 0:
            # add new term to deck
            deck.append(term_queues[score][0])
            # move term to back of the queue
            term_queues[score].append(term_queues[score].pop(0))
            # decrease quota
            quota -= 1
            # log count
            deck_stats.update([score])

    # use any remaining space for score 0's
    # note that the s0 queue does not shift
    for s0_term in term_queues['0']:

        # stop if there is no space for s0 terms
        if len(deck) >= deck_min:
            break

        # add terms to deck
        else:
            deck.append(s0_term)
            deck_stats.update(['0'])

    # shuffle, assemble, and return deck data
    random.shuffle(deck)

    return {'deck':deck,'deck_stats':deck_stats, 'term_queues':term_queues}


def recalibrateTermQueues(terms_dict, term_queues):
    '''
    Adjusts term queues to the terms_dict when a term is changed to a new score.
    Terms are removed from their old queue and added to the new ones.
    New S3 go to the back of the S3 queue and are tagged as 'seen'
        ('seen' S3 are subtracted from total S3 by buildDeck to make room for new S0 terms).
    S0-2 with upgrade go to the back of their queues.
    S0-2 with downgrade go to the back of their queues.
    '''

    # keep stats on logged changes
    recal_stats = collections.Counter()

    # deep copy for iteration; make changes to original term_queues
    tqueues_mirror = copy.deepcopy(term_queues)

    for score, term_queue in tqueues_mirror.items():

        # compare with term_dict, change queue if necessary
        for term in term_queue:

            # most current score, for comparison with old score
            cur_score = terms_dict[term]['score']

            # remove term from old queue and add to new
            if score != cur_score:

                # count for stats
                change = f'{score}->{cur_score}' if int(cur_score) > int(score) \
                             else f'{cur_score}<-{score}'
                recal_stats.update([change])

                # send to back of new queue 
                term_queues[score].remove(term)
                term_queues[cur_score].append(term)
                    
                # add/remove 'seen' tag for '3' upgrades 
                if cur_score != '3' and 'seen' in terms_dict[term]: # remove seen
                    del terms_dict[term]['seen']

                elif cur_score == '3': # add seen
                    terms_dict[term]['seen'] = True

            # move on
            else:
                continue

    # return new queues
    # also return terms_dict with S3 'seen' tags
    return {'terms_dict':terms_dict, 'term_queues':term_queues, 'recal_stats':recal_stats}


def purgeTerms(terms_dict):
    '''
    Reset the 'seen' tag on S3 terms to False at the beginning of a new cycle.
    '''
    for term, term_data in terms_dict.items():
        if term_data['score'] == '3':
            if 'seen' in term_data:
                del term_data['seen']

    return terms_dict

def selectCycle(terms_dict, term_queues):

    '''
    Run an interactive program to select the cycle and deck sizes for a study set.
    Return the cycle size selected by the user.
    '''

    clearDisplay()
    print('Select set properties: \n')
    print(f'There are {len(terms_dict)} terms in the set.\n')

    time.sleep(.5)

    # present user with minimum deck size selection
    deck_min = askQuestion(set(str(i) for i in range(10, 500)),
                           prompt='Enter a minimum deck size from 10-500\n',
                           simple=False,
                           reply='invalid. choose integer between 10-500...\n')


    # prepare data for cycle and deck size selection
    s_counts = dict((score, len(terms)) for score, terms in term_queues.items())  # counts of scores in a deck:


    # present user with selection menu for cycle and deck sizes
    # the program provides live feedback as the user decreases or increases the default cycle size (30)
    cycle = 30  # user selection stored here
    while True:
        # clear terminal display
        clearDisplay()

        # calculate daily deck quotas and deck size based on user input below
        s3_quota = math.ceil(s_counts['3'] / cycle) if '3' in s_counts else 0  # math.ceil rounds up
        s2_quota = math.ceil(s_counts['2'] / 4) if '2' in s_counts else 0
        s1_quota = math.ceil(s_counts['1'] / 2) if '1' in s_counts else 0
        s0_quota = int(deck_min) - (s1_quota + s2_quota + s3_quota) \
                        if int(deck_min) - (s1_quota + s2_quota + s3_quota) >= 0 \
                        else 0 # prevent negative input

        deck_size = s1_quota + s2_quota + s3_quota + s0_quota

        # present user selection screen
        print('\ntype [2] for +, [1] for -, or [y] for accept\n')
        print(f'SELECT CYCLE SIZE --> [ {cycle} ]\n')
        print('-' * 50)
        print('\t' * 2 + 'Session Deck Makeup:\n')
        print('\t' * 2 + f'     size: {deck_size}\n')
        print('score 0\t\tscore 1\t\tscore 2\t\tscore 3')
        print(f'   {s0_quota}\t\t   {s1_quota}\t\t   {s2_quota}\t\t   {s3_quota}\t\n')

        # retrieve and enact user input via set_cycle
        set_cycle = askQuestion({'1', '2', 'y'})

        # accept cycle as is
        if set_cycle == 'y':
            break

        # decrease cycle
        elif set_cycle == '1':

            # decrease by 1 when < 5
            if 1 < cycle <= 5:
                cycle -= 1

            # prevent 0 error if user subtracts below 1
            elif cycle == 1:
                displayNew('minimum cycle of 1...')
                time.sleep(1)

            # subtract by 5
            else:
                cycle -= 5

        # increase cycle
        elif set_cycle == '2':

            # increase by 1 if cycle < 5
            if cycle <= 4:
                cycle += 1

            # add by 5
            else:
                cycle += 5

    return {'cycle_length':cycle, 'deck_min':deck_min}


def validateSet(set_data):
    '''
    Check for valid set data, return set if already initialized.
    If the set is new, embed the terms dict into a set dict with set data.
    Return the new set.
    Return False if the set is not completely scored.
    '''

    # clear terminal display
    clearDisplay()

    # detect new sets
    if 'init_date' not in set_data:
        terms_dict = set_data

        print('New set detected...')
        print('   Beginning setup...')
        time.sleep(.5)
        clearDisplay()

        # reject set if its not fully scored
        scoreless_terms = set(term for term, term_data in terms_dict.items()
                                    if 'score' not in term_data)
        if scoreless_terms:
            print('This set has not been completely scored yet...')
            print('Score the set before running study module.')
            time.sleep(2)
            return False

        # present user with name selection
        set_name = askQuestion({}, prompt='\nEnter a name for the new set:\n',
                                   simple=False)

        # initialize new set data with user input data
        term_queues = createTermQueues(terms_dict)

        # Begin user input program for cycle selection
        cycle_data = selectCycle(terms_dict, term_queues)

        # timestamp for set initialization
        init_date = datetime.now().__str__()

        new_set_data = {'name' : set_name,
                        'init_date' : init_date,
                        'deck_min' : int(cycle_data['deck_min']),
                        'cycle_length' : int(cycle_data['cycle_length']),
                        'total_sessions' : 0,
                        'term_queues' : term_queues,
                        'terms_dict' : terms_dict}

        clearDisplay()
        print('set initialized...')
        time.sleep(1)

        return new_set_data

    # recalibrate sets with completed cycles
    elif set_data['cycle_length'] / set_data['total_sessions'] == 1:
        print('cycle for this set is complete...')
        start_cycle = askQuestion({'y','n'}, prompt=f"start a new study cycle for {set_data['name']}?")

        if start_cycle == 'y':

            keep_cycle = askQuestion({'y', 'n'}, prompt=f"keep cycle length at [ {set_data['cycle_length']} ]?")

            if keep_cycle == 'y':
                print(f"resetting {set_data['name']}...")

                # reset sessions
                set_data['total_sessions'] = 0

                # remark 'seen' to False
                set_data['terms_dict'] = purgeTerms(set_data['terms_dict'])

                # shuffle score 3 terms
                random.shuffle(set_data['term_queues']['3'])

                time.sleep(.5)
                return set_data

            elif keep_cycle == 'n':

                clearDisplay()
                print('resetting cycle length...')
                time.sleep(.5)

                # launch user cycle interaction
                new_cycle_data = selectCycle(set_data['terms_dict'], set_data['term_queues'])

                # reset the terms for a new cycle
                set_data['cycle_length'] = int(new_cycle_data['cycle_length'])
                set_data['deck_min'] = int(new_cycle_data['deck_min'])
                set_data['terms_dict'] = purgeTerms(set_data['terms_dict'])
                random.shuffle(set_data['term_queues']['3']) # shuffle score 3 terms 
                set_data['total_sessions'] = 0

                clearDisplay()
                print('cycle reset...')
                time.sleep(.5)

                return set_data

        elif start_cycle == 'n':
            print('leaving set up module...')
            return False

    # return pre-validated set
    else:
        print('set ready!')
        time.sleep(.5)
        return set_data

def addToTerms(terms, csv_object):

    '''
    Add new terms to an existing terms_dict and their queues.
    Requires standard terms_dict. new_terms is formatted identically.

    TO-DO: add an option for default score or for scoring terms.
    '''

    max_ID = max(int(ID) for ID in terms['terms_dict'])

    for i, term in enumerate(csv_object):


        # assign new ID number
        ID = str(i + max_ID + 1)
        term_text = term[0]
        definition = term[1]

	# add occurrence data 
        occurrences = term[2] if len(term) > 2 else ''
        source = eval(term[3]) if len(term) > 3 else []

        # Add term to terms data
        terms['terms_dict'][ID] = {'term':term_text,
                                   'definition':definition,
                                   'score':'0',
				   'occurrences':occurrences,
                                   'source_lexemes': source
                                    }
        # Add term to the back of the 0 queue
        terms['term_queues']['0'].append(ID)

    return terms
