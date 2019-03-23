'''
This module contains the Study class,
used to launch a study session during a Jupyter notebook/lab session.
The module prepares and consumes data from the Mahir deck handlers and uses Text-Fabric
to display formatted font.
'''

import json, time, random
from datetime import datetime
from tf.app import use
from tf.fabric import Fabric
from IPython.display import clear_output, display, HTML
from ManageSets import buildDeck, purgeTerms, recalibrateTermQueues
from Load import loadExistingSet

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
            self.set_data = json.load(setfile)
        self.vocab_json = vocab_json

        # check cycle length
        run, set_data = self.check_end_cycle(self.set_data)
        if not run:
            self.save_file(self.set_data, vocab_json)
            raise Exception('EXIT PROGRAM INITIATED; FILE SHUFFLED AND SAVED')

        # prep set data
        self.term_queues = self.set_data['term_queues']
        self.terms_dict =  self.set_data['terms_dict']
        cycle_len = self.set_data['cycle_length']
        deck_min = self.set_data['deck_min']
        s3_seen = len([term for term, term_data in self.terms_dict.items()
                          if 'seen' in term_data  # only s3 terms
                          and term_data['seen']
                          and term_data['score'] == '3']) # temporary fix to loophole

        # build the study deck
        deck_data = buildDeck(self.term_queues, s3_seen, deck_min=deck_min, cycle_len=cycle_len)
        self.deck = deck_data['deck']
        deck_stats = deck_data['deck_stats']

        # session report 
        print(set_data['name'], 'ready for study.')
        print(f"this is session {set_data['total_sessions']+1}:")
        for score, stat in deck_stats.items():
            print(f'score {score}: {stat} terms')
        print(f'total: {sum(deck_stats.values())}')

    def learn(self, ex_otype='verse'):
        '''
        Runs a study session with the user.
        '''
        print('beginning study session...')
        start_time = datetime.now()
              
        # begin UI loop
        term_n = 0
        while True:
            term_ID = self.deck[term_n]
            term_text = self.terms_dict[term_ID]['term']
            definition = self.terms_dict[term_ID]['definition']
            score = self.terms_dict[term_ID]['score']
            occurrences = self.terms_dict[term_ID].get('occurrences','') or len(self.terms_dict[term_ID]['custom_lexemes'])
            
            # assemble and select examples (without lex cycling)
#             lexs = self.terms_dict[term_ID].get('source_lexemes', [])
#             cust_lexs = self.terms_dict[term_ID].get('custom_lexemes', [])
#             ex_words = [word for lex in lexs for word in self.L.d(lex, 'word')] + [w[0] for w in cust_lexs]
#             ex_instance = random.choice(ex_words)
#             ex_passage = self.L.u(ex_instance, ex_otype)[0]
              
            # assemble and select examples (WITH lex cycling)
            lexs = self.terms_dict[term_ID]['source_lexemes'] or self.terms_dict[term_ID]['custom_lexemes']
            ex_lex = random.choice(lexs)
            try:
                ex_instance = random.choice(self.L.d(ex_lex, 'word')) if type(ex_lex) != list else ex_lex[0]
            except:
                raise Exception(f'lexs: {lexs}; ex_lex: {ex_lex}')
            ex_passage = self.L.u(ex_instance, ex_otype)[0]
            std_glosses = [(lx, self.F.gloss.v(lx), self.F.freq_lex.v(lx)) for lx in lexs] if type(ex_lex) != list else []
              
            # display passage prompt and score box
            clear_output()
            display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{term_n+1}/{len(self.deck)}</span>'))
              
            highlight = 'lightgreen' if score == '3' else 'pink'
            self.TF.plain(ex_passage, highlights={ex_instance:highlight})

            while True:
                user_instruct = self.good_choice({'', '0', '1', '2', '3', ',', '.', 'q', 'c', 'e'}, ask='')
                
                if user_instruct in {''}:
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:16pt">{term_text}</span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{definition} </span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{score}</span>'))
                    display(HTML(f'<span style="font-family:Times New Roman; font-size:10pt">{std_glosses}</span>'))
                
                # score term
                elif user_instruct in {'0', '1', '2', '3'}:
                    self.terms_dict[term_ID]['score'] = user_instruct
                    term_n += 1
                    break
              
                # move one term back/forward
                elif user_instruct in {',', '.'}:
                    if user_instruct == ',':
                        if term_n != 0:
                            term_n -= 1
                        break
                    elif user_instruct == '.':
                        if term_n != len(self.deck):
                            term_n += 1
                        break
                
                # get a different word context
                elif user_instruct == 'c':
                    break
              
                # edit term definition on the fly
                elif user_instruct == 'e':
                    new_def = self.good_choice(set(), ask=f'edit def [{definition}]')
                    self.terms_dict[term_ID]['definition'] = new_def
                    break
              
                # user quit
                elif user_instruct == 'q':
                    raise Exception('Quit initiated. Nothing saved.')
              
            # launch end program sequence
            if term_n > len(self.deck)-1:
                clear_output()
                ask_end = self.good_choice({'y', 'n'}, 'session is complete, quit now?')
                
                if ask_end == 'y':
                    
                    # adjust term queues to new scores
                    recalibrated_set = recalibrateTermQueues(self.terms_dict, self.term_queues)
                    recal_terms_dict = recalibrated_set['terms_dict']
                    recal_term_queues = recalibrated_set['term_queues']

                    # update set data
                    self.set_data['total_sessions'] += 1
                    self.set_data['terms_dict'] = recal_terms_dict
                    self.set_data['term_queues'] = recal_term_queues
                    self.save_file(self.set_data, self.vocab_json)
                    break
              
                elif ask_end == 'n':
                    term_n -= 1
        
        clear_output()
        print('The following scores were changed ')
        recal_stats = recalibrated_set['recal_stats']
        for change, amount in recal_stats.items():
            print(change, '\t\t', amount)
        # display duration of the session
        end_time = datetime.now()
        duration = end_time - start_time
        print('\nduration: ', duration.__str__())

    def check_end_cycle(self, set_data):
        '''
        Checks whether the deck is finished
        for the cycle. If so, runs a quick
        parameters reassignment session.
        '''

        run_study = True

        if set_data['cycle_length'] / set_data['total_sessions'] == 1:
            print('cycle for this set is complete...')
            keep_same = self.good_choice({'y', 'n'}, ask='keep cycle parameters the same?')

            if keep_same == 'y':
                set_data['total_sessions'] = 0 # reset sessions
                set_data['terms_dict'] = purgeTerms(set_data['terms_dict']) # remark 'seen' to False
                random.shuffle(set_data['term_queues']['3']) # shuffle score 3 terms

            elif keep_same == 'n':
                print('You must reset parameters manually...')
                print('But I will shuffle score 3 data for you now...')
                random.shuffle(set_data['term_queues']['3']) # shuffle score 3 terms
                run_study = False

        return run_study, set_data

    def good_choice(self, good_choices, ask=''):
        '''
        Gathers and checks a user's input against the 
        allowed choices. Runs loop until valid choice provided.
        '''
        choice = input(ask)

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
