import json, time
from Load import loadNewSet, loadExistingSet
from Score import scoreNewTerms
from Study import studySet
from Ui import askQuestion, clearDisplay, runWelcome, displayNew
from ManageSets import validateSet


def runProgram():
    '''
    Run Mahir, display welcome screen, display menu options, wait for input.
    '''

    version = '0.5 Beta'

    with open('config.json') as config_file:
        settings = json.load(config_file)

    # configure settings
    term_set = settings['set']
    delimiter = settings['delimiter']
    set_type = settings['type']

    # load terms
    if set_type == 'new':
        terms = loadNewSet(term_set, delimiter=delimiter)
    elif set_type == 'load':
        terms = loadExistingSet(term_set)

    # Run the Menu Loop
    menu_options = {'score', 'q', 'study'}
    while True:

        # display the welcome text
        runWelcome(version)
        # report on loaded terms

        # print loaded terms report for initialized terms
        if 'init_date' in terms:
            print(f"{len(terms['terms_dict'])} terms loaded from [ {term_set} ]\n")

        # print loaded terms report for new terms
        else:
            print(f'{len(terms)} terms loaded from [ {term_set} ]\n')


        # give user menu choices
        module_selection = askQuestion(menu_options,
                                       prompt=f"type an option: {sorted(menu_options)}\n",
                                       simple=False,
                                       reply=f'invalid...select from {sorted(menu_options)}\n')

        # ** SCORING PROGRAM **
        if module_selection == 'score':

            # confirm scoring program
            confirm_scoring = askQuestion({'y', 'n'},
                                          prompt='Begin scoring terms?')
            if confirm_scoring == 'n':
                print('returning to menu...')

            # launch the scoring program and store output as variable
            elif confirm_scoring == 'y':

                # score terms
                scored_terms = scoreNewTerms(terms)

                # dump the scored terms
                if not term_set.endswith('.json'):
                    clearDisplay()
                    term_set = askQuestion({}, prompt='Name the new set...', simple=False)
                
                with open(term_set, 'w') as outfile:
                    json.dump(scored_terms,
                              outfile,
                              indent=1,
                              ensure_ascii=False)
                

        elif module_selection == 'study':

            # TO DO: remove the clear display and message
            clearDisplay()
            print('Running study module...')
            time.sleep(.5)

            # validate the set
            study_set = validateSet(terms)

            if study_set:
                # feed set to study module
                studySet(study_set)
            else:
                clearDisplay()
                print('returning to menu...')
                time.sleep(.5)

        elif module_selection == 'q':
            print('\nleaving Mahir...')
            break

runProgram()