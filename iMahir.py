'''
This module contains the Study class,
used to launch a study session during a Jupyter notebook/lab session.
The module prepares and consumes data from the Mahir deck handlers and uses Text-Fabric
to display formatted font.


FOR THE FUTURE:
• Design a term object with callable attributes that can be populated from terms_dict.
'''

import collections, json, random, math
from datetime import datetime
from tf.app import use
from tf.fabric import Fabric
from IPython.display import clear_output, display, HTML

class Study:
    '''
    Prepares and consumes data from Mahir 
    and formats it for use in a Jupyter notebook.
    '''

    def __init__(self, vocab_json, tf_app='bhsa', data_version='2017'):
        '''
        vocab_json - a json file formatted with term data for use with Mahir
        data_version - version of the data for Text-Fabric
        '''
        print('preparing TF...')
        TF = Fabric(locations='/Users/cody/github/etcbc/bhsa/tf/2017')
        TF_api = TF.load('''gloss freq_lex''')
        self.TF = use(tf_app, api=TF_api, silent=True)
        self.F, self.T, self.L = self.TF.api.F, self.TF.api.T, self.TF.api.L
        
        # load set data
        with open(vocab_json) as setfile:
            set_data = json.load(setfile)
            self.set_data = set_data

        # prepare for run, check cycle length
        run = self.check_end_cycle(set_data)
        if not run:
            self.save_file(set_data, vocab_json)
            raise Exception('EXIT PROGRAM INITIATED; FILE SHUFFLED AND SAVED')

        # build the study set, prep data for study session
        self.session_data = Session(set_data) # build session data
        self.vocab_json = vocab_json
        
        # preliminary session report
        deck_stats = self.session_data.deck_stats
        print(set_data['name'], 'ready for study.')
        print(f"this is session {set_data['cycle_data']['total_sessions']+1}:")
        for score, stat in deck_stats.items():
            print(f'score {score}: {stat} terms')
        print(f'total: {sum(deck_stats.values())}')

    
    def learn(self, ex_otype='verse'):
        '''
        Runs a study session with the user.
        '''
        print('beginning study session...')
        start_time = datetime.now()
              
        deck = self.session_data.deck
        terms_dict = self.set_data['terms_dict']
              
        # begin UI loop
        term_n = 0
        while True:
            term_ID = deck[term_n]
            term_text = terms_dict[term_ID]['term']
            gloss = terms_dict[term_ID]['gloss']
            score = terms_dict[term_ID]['score']
            
            # assemble and select examples (cycle through lexemes)
            lexs = terms_dict[term_ID]['source_lexemes'] or terms_dict[term_ID]['custom_lexemes']
            ex_lex = random.choice(lexs)
            try:
                ex_instance = random.choice(self.L.d(ex_lex, 'word')) if type(ex_lex) != list else ex_lex[0]
            except:
                raise Exception(f'lexs: {lexs}; ex_lex: {ex_lex}')
            ex_passage = self.L.u(ex_instance, ex_otype)[0]
            std_glosses = [(lx, self.F.gloss.v(lx), self.F.freq_lex.v(lx)) for lx in lexs] if type(ex_lex) != list else []
              
            # display passage prompt and score box
            clear_output()
            display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{term_n+1}/{len(deck)}</span>'))
              
            highlight = 'lightgreen' if int(score)>2 else 'pink'
            self.TF.plain(ex_passage, highlights={ex_instance:highlight})

            while True:
                user_instruct = self.good_choice({'', ',', '.', 'q', 'c', 'e', 'l', '>', '<'}, ask='', allowNumber=True)
                
                # show term glosses and data
                if user_instruct in {''}:
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:16pt">{term_text}</span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{gloss} </span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{score}</span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:10pt">{std_glosses}</span>'))
                
                # score term
                elif user_instruct.isnumeric():
                    terms_dict[term_ID]['score'] = user_instruct
                    term_n += 1
                    break
              
                # move one term back/forward
                elif user_instruct in {',', '.'}:
                    if user_instruct == ',':
                        if term_n != 0:
                            term_n -= 1
                    elif user_instruct == '.':
                        if term_n != len(deck):
                            term_n += 1
                    break
              
                # skip to beginning or end of deck
                elif user_instruct in {'>','<'}:
                    if user_instruct == '>':
                        term_n = len(deck)
                    elif user_instruct == '<':
                        term_n = 0
                    break
              
                # get a different word context
                elif user_instruct == 'c':
                    break
              
                # edit term gloss on the fly
                elif user_instruct == 'e':
                    new_def = self.good_choice(set(), ask=f'edit def [{gloss}]')
                    terms_dict[term_ID]['gloss'] = new_def
                    break
              
                # edit lexeme nodes on the fly
                elif user_instruct == 'l':
                    lexs = terms_dict[term_ID].get('source_lexemes', )
                    new_lexs = self.good_choice(set(), ask=f'edit lex nodes {lexs}')
                    new_lexs = [int(l.strip()) for l in new_lexs.split(',')]
                    terms_dict[term_ID]['source_lexemes'] = new_lexs
                    break
              
                # user quit
                elif user_instruct == 'q':
                    raise Exception('Quit initiated. Nothing saved.')
              
            # launch end program sequence
            if term_n > len(deck)-1:
                clear_output()
                ask_end = self.good_choice({'y', 'n'}, 'session is complete, quit now?')
                
                if ask_end == 'y':
                    self.finalize_session(start_time)              
                    break
              
                elif ask_end == 'n':
                    term_n -= 1
        
        clear_output()
        print('The following scores were changed ')
        for change, amount in self.set_data['stats'][-1]['changes'].items():
            print(change, '\t\t', amount)
        print('\nduration: ', self.set_data['stats'][-1]['duration'])
        
              
    def finalize_session(self, start_time):
        '''
        Updates and saves session data and stats.
        '''
        
        # log session stats
        session_stats = {}
        session_stats['date'] = str(datetime.now())
        session_stats['duration'] = str(datetime.now() - start_time)
        session_stats['deck'] = self.session_data.deck_stats
        session_stats['cycle'] = self.set_data['cycle_data']['ncycle']
        for term in self.session_data.deck:
            self.set_data['terms_dict'][term]['stats']['seen'] += 1 # count term as seen
        
        # reset queues based on changed scores & update stats
        session_stats['changes'] = collections.Counter()
        self.add_new_scores()
        self.update_queues(session_stats['changes']) 
             
        # update set data
        self.set_data['cycle_data']['total_sessions'] += 1      
        self.set_data['stats'].append(session_stats)
              
        # save new data
        self.save_file(self.set_data, self.vocab_json)
              
    def update_queues(self, stats_dict):

        '''
        Adjusts term queues to the terms_dict when a term is changed to a new score.
        Terms are removed from their old queue and added to the new ones.
        All terms go to the back of their respective queues.
        '''

        term_queues = self.set_data['term_queues']
        terms_dict = self.set_data['terms_dict']
              
        for score, term_queue in term_queues.items():
            for term in term_queue:
                
                # compare old/new score, change if needed
                cur_score = terms_dict[term]['score']
                  
                if score != cur_score:

                    # make string for stats count
                    downgrade = int(cur_score) < int(score)
                    change = f'{cur_score}<-{score}' if downgrade else f'{score}->{cur_score}'
              
                    # make records of change
                    stats_dict.update([change])
                    if downgrade:
                        terms_dict[term]['stats']['missed'] += 1

                    # assign new queue position
                    term_queues[score].remove(term)              
                    if cur_score != '0':
                        term_queues[cur_score].append(term) # scores >0 go to back of queue
                    else:
                        term_queues[cur_score].insert(0, term) # score 0 goes to front of queue

                # if no change, move on
                else:
                    continue
              
              
    def check_end_cycle(self, set_data):
        '''
        Checks whether the deck is finished
        for the cycle. If so, runs a quick
        parameters reassignment session.
        '''

        run_study = True

        if set_data['cycle_data']['cycle_length'] / set_data['cycle_data']['total_sessions'] == 1:
            print('cycle for this set is complete...')
            keep_same = self.good_choice({'y', 'n'}, ask='keep cycle parameters the same?')

            if keep_same == 'y':
                set_data['cycle_data']['total_sessions'] = 0 # reset sessions
                set_data['cycle_data']['ncycle'] += 1
              
                # some scores reset at cyclic intervals (e.g. S3 and S4)
                # this config allows those scores to be reset on a modulo trigger
                for score, configdata in set_data['scoreconfig'].items():
                    ncycle = set_data['cycle_data']['ncycle']
                    nreset = configdata['nreset']
                    shuffle = configdata['shuffle']
                    if ncycle % nreset == 0:
                        if shuffle == 'yes':
                            random.shuffle(set_data['term_queues'][score])
                        set_data['cycle_data']['score_starts'][score] = len(set_data['term_queues'][score])
              
            elif keep_same == 'n':
                print('You must reset parameters manually...')
                run_study = False

        return run_study

    def add_new_scores(self):
        '''
        Adds any new scores to the vocab set
        by checking term scores against term queues and score config.
        '''
        queues = self.set_data['term_queues']
        score_configs = self.set_data['scoreconfig']
        terms_dict = self.set_data['terms_dict']
              
        # add new scores and terms to term queues
        for termID, tdata in terms_dict.items():
            score = tdata['score']
            if score not in queues:
                if score not in score_configs:
                    print(f'CAUTION: score {score} is not configured! (found on term {termID})')
                    print('NB: a new score queue has been generated!')
                queues[score] = []
                self.set_data['cycle_data']['score_starts'][score] = 0
              
    def good_choice(self, good_choices, ask='', allowNumber=False):
        '''
        Gathers and checks a user's input against the 
        allowed choices. Runs loop until valid choice provided.
        '''
        choice = input(ask)
     
        if allowNumber and choice.isnumeric(): # allow arbitrary score choices
            good_choices.add(choice)
            
        while (not {choice} & good_choices) and (good_choices):
            print(f'Invalid. Choose from {good_choices}')
            choice = input(ask)

        return choice

    def save_file(self, set_data, file):
        '''
        Save json set dat with proper encoding
        and indentation.
        '''
        with open(file,'w') as outfile:
            json.dump(set_data, outfile, indent=1, ensure_ascii=False)

              
class Session:

    '''
    Constructs a study set for a session that contains words scored 0-3.
    term_queues is a dict with scores as keys, lists as values containing term IDs.
    deck_max defines when S0 (new) cards should be inserted into a deck. (deck_max - deck_min = available_space).
    cycle_len is the number of days in a full review cycle that class should calculate.

    The key to buildDeck is the term queue.
    The term queue is a list of term IDs of a given score.
    These lists are modified while a deck is constructed.
    When class adds terms to a deck, it also moves them to the end of their queue (with list.pop(0)).
    The modified lists are then returned (along with the deck) to be used for the next study session.
    The cycle is repeated in the subsequent session.
    '''
    
    def __init__(self, set_data):

        # grab set data
        term_queues = set_data['term_queues']
        deck_min = set_data['cycle_data']['deck_min']
        cycle_len = set_data['cycle_data']['cycle_length']
        nsession = set_data['cycle_data']['total_sessions']
        s_starts = set_data['cycle_data']['score_starts'] # sum of scores at start of the cycle
        s_counts = dict((score, len(terms)) for score, terms in term_queues.items()) # sum of all scores by this session

        # calculate daily set quotas, NB math.ceil rounds up^
        # score 4 formula optimizes with decimal issues in Python
        # formula is: int(round(((nterms/nsessions/nreset)*(NthSession-1))-int((nterms/nsessions/nreset)*(NthSession-1)) + (nterms/nsessions/nreset), 2))
              
        score2quota = {'4': int(round(((s_starts['4']/cycle_len/2)*(nsession-1))-int((s_starts['4']/cycle_len/2)*(nsession-1))\
                                + (s_starts['4']/cycle_len/2), 2)) if s_counts.get('4', 0) else 0,     # s4 seen every 2 cycles
                       '3': math.ceil(s_starts['3'] / cycle_len) if s_counts.get('3', 0) else 0,       # s3 seen every cycle
                       '2': math.ceil(s_counts['2'] / 4) if s_counts.get('2', 0) else 0,               # s2 seen every 4 sessions
                       '1': math.ceil(s_counts['1'] / 2) if s_counts.get('1', 0) else 0,               # s1 seen ever other session
                       } 

        # construct a study deck and keep stats
        deck = []

        deck_stats = collections.Counter()

        # add quotas from scores 1-4 and advance queues
        for score, quota in score2quota.items():
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

        # shuffle deck data
        random.shuffle(deck)

        # make session data available to class
        self.deck = deck
        self.deck_stats = deck_stats
        self.term_queues = term_queues