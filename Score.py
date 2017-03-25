import time
from Ui import askQuestion, displayNew, clearDisplay

def scoreNewTerms(terms_dict):

    '''
    Launch an interactive program which cycles through all terms in terms_dict,
    user scores terms 0-3, 0 being unknown, 3 being well-known.
    The scores are used to construct decks for study sessions (cf. decks.buildDeck)

    scoreNewTerms will pick up where user last left off at to score remaining un-scored terms.
    '''

    # number of scored terms during session
    score_count = 0

    clearDisplay()
    print('\nBeginning term scoring...\n')
    time.sleep(1)
    clearDisplay()

    # run scoring program
    while True:

        print('For each term, select a number 0-3 based on your familiarity with it...')
        print('0 being least familiar, 3 being very familiar.')
        print('\ndefinition - [SPACE]\tscore - [0-3]\tedit previous - [e]\tconfirm - [y/n]\tquit - [q]\n')
        time.sleep(.5)

        # ** begin scoring terms **
        run_score = True
        last_term = None # for corrections

        for term, term_data in terms_dict.items():

            # end term scoring
            if not run_score:
                break

            # skip if already scored
            if 'score' in term_data:
                continue

            term_text = term_data['term']
            definition = term_data['definition']

            # present term to user for scoring
            displayNew(term_text)

            while run_score:

                score_commands =  {'0','1','2','3',
                                   'e', ' ', 'q'}

                # print term and ask for score
                score_input = askQuestion(score_commands)

                # QUIT PROGRAM
                if score_input == 'q':

                    confirm_quit = askQuestion({'y','n'},
                                               prompt='\x1b[2K\r' + ' quit scorer and save results?')

                    if confirm_quit == 'y':
                        run_score = False
                        break

                    elif confirm_quit == 'n':
                        print(term_text)

                # display definition
                elif score_input == ' ':
                    print('\t\t' + definition, end='\r')

                # save the score and move on
                elif score_input.isnumeric():
                    score_count += 1
                    term_data['score'] = score_input
                    last_term = term
                    break

                # EDIT PREVIOUS
                elif score_input == 'e':
                    displayNew('editing previous score...')
                    time.sleep(.5)
                    pTerm_text = terms_dict[last_term]['term'] # previous term's text

                    # get the new score input
                    while True:
                        # ask for score
                        new_score = askQuestion({'0','1','2','3'},
                                                  prompt=f'\x1b[2K\rinput new score for {pTerm_text}')

                        # ask for confirmation
                        confirm_change = askQuestion({'y','n'},
                                                       prompt=f"\x1b[2K\rchange from {terms_dict[last_term]['score']} to {new_score}?")

                        # make change if confirmed
                        if confirm_change == 'y':
                            terms_dict[last_term]['score'] = new_score
                            displayNew('change logged...')
                            time.sleep(.5)
                            displayNew(f'{term_text}')
                            break

                        # resume if no change desired
                        else:
                            displayNew('resuming current term')
                            time.sleep(.5)
                            displayNew(f'{term_text}')
                            break
        clearDisplay()
        time.sleep(1)
        print(f'{score_count} terms have been scored and saved')
        break

    return terms_dict