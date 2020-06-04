'''
This module contains the Study class,
used to launch a study session during a Jupyter notebook/lab session.
The module prepares and consumes data from the Mahir deck handlers and uses Text-Fabric
to display formatted font.


FOR THE FUTURE:
• Design a term object with callable attributes that can be populated from terms_dict.
'''

import os
from pathlib import Path
import pickle
import collections
import json
import random
import time
import math
import copy
from datetime import datetime, timedelta
from tf.app import use
from tf.fabric import Fabric
from IPython.display import clear_output, display, HTML

def safediv(a, b):
    '''Return zero in zero divisions'''
    try:
        return a/b
    except ZeroDivisionError:
        return 0

def loadStudy(vocab_json, tf_app='bhsa'):
        """Determine how to load a study session"""

        vocab_json = Path(vocab_json)
        
        # check for existing saves
        savefile = next(Path().glob(f'{vocab_json.stem}.save'), None)
        # check for expiration of save
        # if expired, delete the save (!)
        # this is a little extra motivation to finish each day
        if savefile is not None:
            lastmod = datetime.fromtimestamp(os.path.getmtime(savefile))
            elapsed = ((datetime.now() - lastmod).total_seconds() / 60) / 60
            
            # disable file deletions for now
            if False: #elapsed > 15:
                print('\nOld session found but expired! Deleting it!\n')
                savefile.unlink() # bye bye :) 

        # load the save
        if savefile is not None and savefile.exists():
            with open(savefile, 'rb') as infile:
                savedata = pickle.load(infile)
            return Study(
                vocab_json, 
                tf_app, 
                set_data=savedata['set_data'],
                session_data=savedata['session_data'],
                resume_time=savedata['resume_time'],
                term_n=savedata['term_n'],
                pause_times=savedata['pause_times'],
            )
            
        # load new session
        else:
            return Study(vocab_json, tf_app)
        
    
class Study:
    '''
    Prepares and consumes data from Mahir 
    and formats it for use in a Jupyter notebook.
    '''

    def __init__(self, vocab_json, tf_app='bhsa', 
                 set_data=None, session_data=None,
                 resume_time=False, term_n=0, 
                 pause_times=[]):

        # set meta data for study loop (for saves)
        self.session_data = session_data
        self.set_data = set_data
        self.term_n = term_n
        self.pause_times = pause_times

        self.tf_app = tf_app
        self.fstem = vocab_json.stem # for save names
        
        # load set data
        if not set_data:
            with open(vocab_json) as setfile:
                set_data = json.load(setfile)
                self.set_data = set_data
        
        # retrieve TF app data
        appdata = set_data['app_data']
        app = appdata['app']
        datversion = appdata['version']
        self.glossfeat = appdata['gloss_feature']
        self.freqfeat = appdata['freq_feature']
        self.wordtype = appdata['wordtype']
        self.context = appdata['context']
        
        # load the app
        print('preparing TF...')
        self.TF = use(app, version=datversion, silent=True)
        self.F, self.T, self.L = self.TF.api.F, self.TF.api.T, self.TF.api.L

        # prepare for run, check cycle length
        run = self.check_end_cycle(set_data)
        if not run:
            self.save_file(set_data, vocab_json)
            raise Exception('EXIT PROGRAM INITIATED; FILE SHUFFLED AND SAVED')

        # build the study set, prep data for study session
        if session_data is None:
            self.session_data = Session(set_data)  # build session data
        self.vocab_json = vocab_json

        if resume_time:
            print(f'\nSession is resumed from {resume_time}.\n')
        
        # preliminary session report
        deck_stats = self.session_data.deck_stats
        print(set_data['name'], 'ready for study.')
        print(f"this is session {set_data['cycle_data']['total_sessions']+1}:")
        for score, stat in deck_stats.items():
            print(f'score {score}: {stat} terms')
        print(f'total: {sum(deck_stats.values())}')

    def learn(self):
        '''
        Runs a study session with the user.
        '''
        print('beginning study session...')
        self.start_time = datetime.now() # to be filled in on first instructions
        
               
        def pause_time():
            """Pause the timer"""
            this_duration = datetime.now() - self.start_time
            self.pause_times.append(this_duration)
            self.start_time = None # reset clock

        deck = self.session_data.deck
        terms_dict = self.set_data['terms_dict']

        # make shortform TF methods / data names
        glossfeat, freqfeat, wordtype, context = self.glossfeat, self.freqfeat, self.wordtype, self.context
        F, L, T, Fs = self.F, self.L, self.T, self.TF.api.Fs
        
        # allow toggling of progress indicator
        show_progress = True

        # begin UI loop
        term_n = self.term_n
        while True:
              
            # get term data
            term_ID = deck[term_n]
            term_text = terms_dict[term_ID]['term']
            gloss = terms_dict[term_ID]['gloss']
            score = terms_dict[term_ID]['score']
            missed = terms_dict[term_ID]['stats']['missed']

            # -- assemble and select examples (cycle through lexemes) -- 
            lexs = terms_dict[term_ID]['source_lexemes']
            ex_lex = random.choice(lexs)
            ex_instance = random.choice(L.d(ex_lex, wordtype))
            ex_passage = L.u(ex_instance, context)[0]
            std_glosses = [(lx, Fs(glossfeat).v(lx), Fs(freqfeat).v(lx))
                               for lx in lexs]
            
            # build parse string for BHSA app
            if self.TF.appName == 'bhsa':
                gender = F.gn.v(ex_instance)
                number = F.nu.v(ex_instance)
                if F.pdp.v(ex_instance) == 'verb':
                    person = F.ps.v(ex_instance)
                    stem = F.vs.v(ex_instance)
                    tense = F.vt.v(ex_instance)
                    parse_string = f'{stem}.{tense}.{person}.{gender}.{number}'
                else:
                    state = F.st.v(ex_instance)
                    parse_string = f'{gender}.{number}.{state}'
            
            # -- display passage prompt and score box -- 
            clear_output()
            
            if show_progress:
                display(
                    HTML(f'<span style="font-family:Times New Roman; font-size:14pt">{term_n+1}/{len(deck)}</span>')
                )

            highlights = {'0': 'pink'}
            highlight = highlights.get(score, 'lightgreen') # default to light green

            passage = self.TF.sectionStrFromNode(ex_passage)
            display(HTML(
                f'<span style="float:right; font-family:Times New Roman; font-size:14pt">{passage}<span>'))
            self.TF.plain(ex_passage, highlights={ex_instance: highlight})

            # -- get user input --
            while True:
                user_instruct = self.good_choice(
                    {'', ',', '.', 'q', 'c', 
                     'e', 'l', '>', '<', 'p',
                     'save', 'hprog'}
                    , ask='', allowNumber=True)
                
                # start timer upon user instruct if not already
                if self.start_time is None:
                    self.start_time = datetime.now()
              
                # show term glosses and data
                if user_instruct in {''}:
                    display(HTML(
                        f'<span style="font-family:Times New Roman; font-size:16pt">{term_text}</span>'))
                    display(HTML(
                        f'<span style="font-family:Times New Roman; font-size:14pt">{gloss} </span>'))

                    # show parse string for BHSA app
                    if self.TF.appName == 'bhsa':
                        display(HTML(
                            f'<span style="font-family:Times New Roman; font-size:10pt">{parse_string} </span>')
                        )

                    display(HTML(
                        f'<span style="font-family:Times New Roman; font-size:14pt">{score}</span>'))
                    display(HTML(
                        f'<span style="font-family:Times New Roman; font-size:10pt">{std_glosses}</span>'))
                    display(HTML(
                        f'<span style="font-family:Times New Roman; font-size:10pt">missed: {missed}</span>'))

                # score term
                elif user_instruct.isnumeric():
                    
                    if user_instruct not in self.set_data['term_queues']:
                        confirm = self.good_choice({'y','n'}, ask=f'Add new score [{user_instruct}]?')
                        if confirm == 'y':
                            pass
                        else:
                            break
                    
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
                elif user_instruct in {'>', '<'}:
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
                    new_def = self.good_choice(
                        set(), ask=f'edit def [{gloss}]')
                    terms_dict[term_ID]['gloss'] = new_def
                    break

                # edit lexeme nodes on the fly
                elif user_instruct == 'l':

                    # confirm lexeme edit
                    confirm = self.good_choice({'y','n'}, ask='Edit lex nodes?')
                    if confirm == 'n':
                        break

                    lexs = terms_dict[term_ID].get('source_lexemes', )
                    new_lexs = self.good_choice(
                        set(), ask=f'edit lex nodes {lexs}')
                    new_lexs = [int(l.strip()) for l in new_lexs.split(',')]
                    terms_dict[term_ID]['source_lexemes'] = new_lexs
                    break
              
                # pause timer
                elif user_instruct == 'p':
                    pause_time()
                    self.save_session(term_n) # save a back up just in case
                    print('Session time paused...')

                # allow for saving sessions
                elif user_instruct == 'save':
                    pause_time()
                    self.save_session(term_n)
                    print('Session saved for 15 hours...')
                    print(f'\telapsed: {sum(self.pause_times, timedelta())}')
                    return

                # user quit
                elif user_instruct == 'q':
                    confirm = self.good_choice({'y', 'n'}, ask='confirm quit?') # double check
                    if confirm == 'y':
                        raise Exception('Quit initiated. Nothing saved.')
                    else:
                        break

                # toggle progress indicator
                elif user_instruct == 'hprog':
                    show_progress = not show_progress
                    break

            # launch end program sequence
            if term_n > len(deck)-1:
                clear_output()
                ask_end = self.good_choice(
                    {'y', 'n'}, 'session is complete, quit now?')

                if ask_end == 'y':
                    times = [datetime.now() - self.start_time] + self.pause_times
                    self.finalize_session(times)
                    break

                elif ask_end == 'n':
                    term_n -= 1

        clear_output()
        print('The following scores were changed ')
        for change, amount in self.set_data['stats'][-1]['changes'].items():
            print(change, '\t\t', amount)
        print('\nduration: ', self.set_data['stats'][-1]['duration'])
        print('\nseconds per term:', self.set_data['stats'][-1]['secs_per_term'])

    def save_session(self, term_n):
        """Save a session for later."""
        savedata = {
            'set_data': self.set_data,
            'session_data': self.session_data,
            'resume_time': str(datetime.now()),
            'pause_times': self.pause_times,
            'term_n': term_n,
        }
        with open(f'{self.fstem}.save', 'wb') as outfile:
            pickle.dump(savedata, outfile)
            
    def clean_session_saves(self):
        """Checks for saves and removes them"""
        savefile = next(Path().glob(f'{self.fstem}.save'), None)
        if savefile is not None and savefile.exists():
            savefile.unlink()
            
    def finalize_session(self, times):
        '''
        Updates and saves session data and stats.
        '''
        
        # log session stats
        session_stats = {}
        duration = sum(times, timedelta())
        secs_per_term = round(duration.total_seconds() / len(self.session_data.deck), 2) # average seconds per term
        session_stats['date'] = str(datetime.now())
        session_stats['duration'] = str(duration) 
        session_stats['secs_per_term'] = secs_per_term
        session_stats['deck'] = self.session_data.deck_stats
        session_stats['cycle'] = self.set_data['cycle_data']['ncycle']
        for term in self.session_data.deck:
            # count term as seen
            self.set_data['terms_dict'][term]['stats']['seen'] += 1

        # reset queues based on changed scores & update stats
        session_stats['changes'] = collections.Counter()
        self.add_new_scores()
        self.update_queues(session_stats['changes'])
        # track final score count at end of session
        session_stats['score_counts'] = dict((score, len(queue))
                                             for score, queue in self.set_data['term_queues'].items())

        # update set data
        self.set_data['cycle_data']['total_sessions'] += 1
        self.set_data['stats'].append(session_stats)

        # save new data
        self.save_file(self.set_data, self.vocab_json)
        self.clean_session_saves()

    def update_queues(self, stats_dict):
        '''
        Adjusts term queues to the terms_dict when a term is changed to a new score.
        Terms are removed from their old queue and added to the new ones.
        All terms go to the back of their respective queues.
        '''

        term_queues = self.set_data['term_queues']
        terms_dict = self.set_data['terms_dict']
        # make buffer queues for iteration
        # prevents altering original during iteration
        buffer_queues = copy.deepcopy(term_queues)

        # make adjustments
        for score, term_queue in buffer_queues.items():
            for term in term_queue:

                cur_score = terms_dict[term]['score']
              
                # compare old/new score, change if needed
                if score != cur_score:

                    # check for certain term changes
                    isdowngrade = int(cur_score) < int(score)
                    change = f'{cur_score}<-{score}' if isdowngrade else f'{score}->{cur_score}'
                    missed = (
                        int(cur_score) < int(score)
                        and int(score) > 2
                    )
                    learned = (
                        int(score) < 3 
                        and int(cur_score) > 2
                        and terms_dict[term]['stats']['missed'] == 0 
                    )

                    # make records of missed or learned terms
                    stats_dict.update([change])
                    if missed:
                        terms_dict[term]['stats']['missed'] += 1
                    if learned:
                        terms_dict[term]['stats']['learned'] = str(datetime.now()) 

                    # assign new queue position
                    term_queues[score].remove(term)
                    if cur_score != '0':
                        # scores >0 go to back of queue
                        term_queues[cur_score].append(term)
                    else:
                        # score 0 goes to front of queue
                        term_queues[cur_score].insert(0, term)

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

        if safediv(set_data['cycle_data']['cycle_length'], set_data['cycle_data']['total_sessions']) == 1:
            print('cycle for this set is complete...')
            keep_same = self.good_choice(
                {'y', 'n'}, ask='keep cycle parameters the same?')

            if keep_same == 'y':
                set_data['cycle_data']['total_sessions'] = 0  # reset sessions
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
                        set_data['cycle_data']['score_starts'][score] = len(
                            set_data['term_queues'][score])

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
                    print(
                        f'CAUTION: score {score} is not configured! (found on term {termID})')
                    print('NB: a new score queue has been generated!')
                queues[score] = []
                self.set_data['cycle_data']['score_starts'][score] = 0

    def good_choice(self, good_choices, ask='', allowNumber=False):
        '''
        Gathers and checks a user's input against the 
        allowed choices. Runs loop until valid choice provided.
        '''
        choice = input(ask)

        if allowNumber and choice.isnumeric():  # allow arbitrary score choices
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
        with open(file, 'w') as outfile:
            json.dump(set_data, outfile, indent=1, ensure_ascii=False)


class Session:

    '''
    Constructs a study set for a session that contains words scored 0-3.
    term_queues is a dict with scores as keys, lists as values containing term IDs.
    The quota for term 0 (new terms) is set by the user in the new_quota key of cycle_data.
    The cycle_len is the number of days in a full review cycle that class should calculate.

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
        new_min = set_data['cycle_data']['new_quota']
        cycle_len = set_data['cycle_data']['cycle_length']
        nsession = set_data['cycle_data']['total_sessions']
        # sum of scores at start of the cycle
        s_starts = set_data['cycle_data']['score_starts']
        # sum of all scores by this session
        s_counts = dict((score, len(terms))
                        for score, terms in term_queues.items())

        # calculate daily set quotas, NB math.ceil rounds up^
        # score 4-5 formula optimizes with decimal issues in Python
        # formula is: int(round(((nterms/nsessions/nreset)*(NthSession-1))-int((nterms/nsessions/nreset)*(NthSession-1)) + (nterms/nsessions/nreset), 2))

        score2quota = {
            # s6 seen every 8 cycles
            '6': int(round(((s_starts['6']/cycle_len/8)*(nsession-1))-int((s_starts['6']/cycle_len/8)*(nsession-1))
              + (s_starts['6']/cycle_len/8), 2)) if s_counts.get('6', 0) else 0,
            # s5 seen every 4 cycles
            '5': int(round(((s_starts['5']/cycle_len/4)*(nsession-1))-int((s_starts['5']/cycle_len/4)*(nsession-1))
                          + (s_starts['5']/cycle_len/4), 2)) if s_counts.get('5', 0) else 0,
            # s4 seen every 2 cycles
            '4': int(round(((s_starts['4']/cycle_len/2)*(nsession-1))-int((s_starts['4']/cycle_len/2)*(nsession-1))
                          + (s_starts['4']/cycle_len/2), 2)) if s_counts.get('4', 0) else 0,
            # s3 seen every cycle
            '3': math.ceil(s_starts['3'] / cycle_len) if s_counts.get('3', 0) else 0,
            # s2 seen every 4 sessions
            '2': math.ceil(s_counts['2'] / 4) if s_counts.get('2', 0) else 0,
            # s1 seen ever other session
            '1': math.ceil(s_counts['1'] / 2) if s_counts.get('1', 0) else 0,
            # s0 set by user
            '0': new_min
        }

        # construct a study deck and keep stats
        deck = []

        deck_stats = collections.Counter()

        # add quotas from scores and advance known queues
        for score, quota in score2quota.items():
            for i in range(0, quota):

                # stop if no more terms
                if len(term_queues[score]) < i+1:
                    break

                # add new terms to deck
                # move known terms to back of their queues
                if score != '0':
                    deck.append(term_queues[score][0])
                    term_queues[score].append(term_queues[score].pop(0))

                # score 0 selected differently; their queue is not advanced
                else:
                    deck.append(term_queues[score][i])

                # log count for statistics tracking
                deck_stats.update([score])

        # shuffle deck data
        random.shuffle(deck)

        # make session data available to class
        self.deck = deck
        self.deck_stats = deck_stats
        self.term_queues = term_queues
