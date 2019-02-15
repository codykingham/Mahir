import json, time, csv
from Load import loadNewSet, loadExistingSet
from Score import scoreNewTerms
from Study import studySet
from Ui import askQuestion, clearDisplay, runWelcome, displayNew
from ManageSets import validateSet, addToTerms
from tf.fabric import Fabric


def runProgram():
    '''
    Run Mahir, display welcome screen, display menu options, wait for input.
    '''

    version = '0.80 Beta'

    with open('config.json') as config_file:
        settings = json.load(config_file)

    # configure settings
    term_set = settings['set']
    delimiter = settings['delimiter']
    set_type = settings['type']
    tf_location = settings['tf_location']
    tf_module = settings['tf_module']

    # TEMPORARY FIX FOR TEXT FABRIC LOAD
    # MUST AVOID TF LOAD WITH GREEK DATASET
    # SHOULD IMPLEMENT NEW LOADING SYSTEM TO SOLVE THIS WORKAROUND
    if 'hebrew' in term_set:
        print('\nPreparing Text-Fabric Data for Mahir...\n\n')
        TF = Fabric(locations=tf_location, modules=tf_module)
        tf_api = TF.load('')
        time.sleep(1)
    else:
        tf_api = None

    # load terms
    if set_type == 'new':
        terms = loadNewSet(term_set, delimiter=delimiter)
    elif set_type == 'load':
        terms = loadExistingSet(term_set)

    # Run the Menu Loop
    menu_options = {'score', 'q', 'study', 'add'}
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

        # SCORING
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
                
        # STUDY
        elif module_selection == 'study':

            # TO DO: remove the clear display and message
            clearDisplay()
            print('Running study module...')
            time.sleep(.15)

            # validate the set
            study_set = validateSet(terms)

            if study_set:
                # feed set to study module
                studySet(study_set, term_set, tf_api) 
            else:
                clearDisplay()
                print('returning to menu...')
                time.sleep(.15)

        # ADD
        elif module_selection == 'add':

            valid_path = False

            while True:
                clearDisplay()
                print('Enter a valid pathway or "q" to quit...\n')
                add_file = askQuestion({},
                            prompt='enter the path to the new terms file...\n',
                            confirm=True,
                            simple=False)

                try:
                    new_terms_file = open(add_file, 'r')
                    valid_path = True

                except FileNotFoundError:
                    if add_file != 'q':
                        clearDisplay()
                        print('file not found! Please re-enter the path...')
                        time.sleep(1)

                if valid_path:
                    break

                elif add_file == 'q':
                    break

            if valid_path:
                num_old_terms = len(terms['terms_dict'])

                new_terms = csv.reader(new_terms_file, delimiter=',')
                new_terms_data = addToTerms(terms, new_terms)

                print(f'\n{len(new_terms_data["terms_dict"]) - num_old_terms} new terms detected...')

                time.sleep(.5)

                with open(term_set, 'w') as outfile:
                    json.dump(new_terms_data,
                              outfile,
                              indent=1,
                              ensure_ascii=False)

                print('\nterms added!')

                time.sleep(2)

        # QUIT
        elif module_selection == 'q':
            print('\nleaving Mahir...')
            break



runProgram()
