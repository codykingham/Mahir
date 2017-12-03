import time, json
from Ui import askQuestion, displayNew, clearDisplay
from ManageSets import buildDeck, recalibrateTermQueues
from getch import getch
from datetime import datetime

def studySet(set_data, outfile):

    '''
    Launch an interactive program which cycles through all terms in terms_dict,
    user scores terms 0-3, 0 being unknown, 3 being well-known.
    The scores are used to construct decks for study sessions (cf. decks.buildDeck)

    scoreNewTerms will pick up where user last left off at to score remaining un-scored terms.
    '''

    # retrieve set data
    term_queues = set_data['term_queues']
    terms_dict =  set_data['terms_dict']
    cycle_len = set_data['cycle_length']
    deck_min = set_data['deck_min']
    s3_seen = len([term for term, term_data in terms_dict.items()
                        if 'seen' in term_data  # only s3 terms
                        and term_data['seen']
                        and term_data['score'] == '3']) # temporary fix to loophole

    # build the study deck
    deck_data = buildDeck(term_queues, s3_seen, deck_min=deck_min, cycle_len=cycle_len)
    deck = deck_data['deck']
    deck_stats = deck_data['deck_stats']

    clearDisplay()
    print(f"\nbeginning study session {set_data['total_sessions']+1}...\n")
    time.sleep(1)
    clearDisplay()

    # start a timer
    start_time = datetime.now()

    # ** begin reviewing terms **
    run_review = True
    last_term = None  # for corrections

    time.sleep(.3)
    progress = 0
    for term in deck:

        clearDisplay()

        # display deck name and statistics
        print(set_data['name'])
        for score, stat in deck_stats.items():
            print(f'score {score}: {stat} terms')
        print(f'total: {sum(deck_stats.values())}')

        # display control information
        print('\ndefinition - [SPACE]\tscore - [0-3]\tedit previous - [e]\tconfirm - [y/n]\tquit - [q]\n')

        progress += 1

        # display progress bar
        completion = '*' * progress
        remaining = ' ' * (len(deck)-progress)
        print('[{}{}]\n'.format(completion,
                                remaining))


        # end term scoring
        if not run_review:
            break

        term_text = terms_dict[term]['term']
        term_formatted = '\n\t\t\t\t\t' + term_text
        definition = terms_dict[term]['definition']
        score = terms_dict[term]['score']
        occurrences = terms_dict[term]['occurrences'] if 'occurrences' in terms_dict[term] else ''

        # present term to user for scoring
        displayNew('\n'+term_formatted)

        while run_review:

            score_commands = {'0', '1', '2', '3',
                              'e', ' ', 'q'}

            # print term and ask for score
            score_input = askQuestion(score_commands)

            # QUIT PROGRAM
            if score_input == 'q':

                confirm_quit = askQuestion({'y', 'n'},
                                           prompt='\x1b[2K\r' + ' quit review?')

                # TODO: switch to the askQuestion confirm arg and remove two bottom steps
                if confirm_quit == 'y':
                    run_review = False
                    break

                elif confirm_quit == 'n':
                    print(term_text)

            # display definition
            elif score_input == ' ':
                print(f'\n\n\t\t\t\t\t{definition} ({occurrences})')
                print(f'\n\t\t\t\t\t{score}')


            # save the score and move on
            elif score_input.isnumeric():
                terms_dict[term]['score'] = score_input
                last_term = term
                break

            # EDIT PREVIOUS
            elif score_input == 'e':
                displayNew('editing previous score...')
                time.sleep(.3)
                pTerm_text = terms_dict[last_term]['term']  # previous term's text

                # get the new score input
                while True:
                    # ask for score
                    new_score = askQuestion({'0', '1', '2', '3'},
                                            prompt=f'\x1b[2K\rinput new score for {pTerm_text}')

                    # ask for confirmation
                    confirm_change = askQuestion({'y', 'n'},
                                                 prompt=f"\x1b[2K\rchange from {terms_dict[last_term]['score']} to {new_score}?")

                    # make change if confirmed
                    if confirm_change == 'y':
                        terms_dict[last_term]['score'] = new_score
                        displayNew('change logged...')
                        time.sleep(.3)
                        displayNew(term_formatted)
                        break

                    # resume if no change desired
                    else:
                        displayNew('resuming current term')
                        time.sleep(.3)
                        displayNew(term_formatted)
                        break

    # Save changes. But only on a complete session
    if run_review:

        # adjust term queues to new scores
        recalibrated_set = recalibrateTermQueues(terms_dict, term_queues)
        recal_terms_dict = recalibrated_set['terms_dict']
        recal_term_queues = recalibrated_set['term_queues']

        # update set data
        set_data['total_sessions'] += 1
        set_data['terms_dict'] = recal_terms_dict
        set_data['term_queues'] = recal_term_queues

        # save set file
        name = set_data['name']
        with open(outfile,'w') as ofile:
            json.dump(set_data,
                      ofile,
                      indent=1,
                      ensure_ascii=False)

        while True:
            # display logged changes and duration of session
            clearDisplay()
            print('The following scores were changed ')
            recal_stats = recalibrated_set['recal_stats']
            for change, amount in recal_stats.items():
                print(change, '\t\t', amount)
            
            # display duration of the session
            end_time = datetime.now()
            duration = end_time - start_time
            print('\nduration: ', duration.__str__(), '\n')

            print('press any button to proceed...')
            proceed = getch()

            break

    clearDisplay()
