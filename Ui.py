from getch import getch
import os, time

def runWelcome(version):
    '''
    Displays the Mahir welcome screen.
    '''
    clearDisplay()
    # Welcome Screen
    print('\n                  ~~~~MAHIR~~~~')
    time.sleep(0.1)
    print(f'                version {version}')
    time.sleep(0.1)
    print('        © 2018 Cody Kingham, the Unlicense')

    # display flying Hebrew text
    magic_line = '     הוּא עֶזְרָא עָלָה מִבָּבֶל וְהוּא־סֹפֵר מָהִיר בְּתוֹרַת משֶׁה '
    fly_line = ''
    for letter in magic_line:
        fly_line += letter
        time.sleep(0.005)
        print(fly_line, end='\r')
    print('\n')
    time.sleep(.3)

def displayNew(display_string):
    '''
    Replaces previous output with a new output string in the terminal.
    Writes new output on the same line.
    '''

    # add ANSI code for resetting previous display
    display_string = '\x1b[2K\r' + display_string

    # print on same line
    print(display_string, end='\r')

def askQuestion(responses, simple=True, prompt='', reply='', confirm=False):
    '''
    Run a question loop and wait for an answer;
    requires set of valid responses; optional prompt string.
    If answer is not valid, prompt user for valid input.
    Return the valid answer.

    simple is default; answers are 1 keystroke;
    simple=False means typed answers + ENTER
    '''

    # present user with prompt
    if prompt:
        displayNew(prompt)

    # run ask cycle
    while True:
        answer = getch() if simple else input()

        # check against valid inputs
        if responses:

            if answer not in responses:
                # display reply
                if reply:
                    displayNew(reply)
                else:
                    displayNew(f'Please chose from {sorted(responses)}...')

            # return answer
            else:
                return answer


        # any input is valid, but confirm first
        else:
            confirm = askQuestion({'y','n'}, prompt=f'confirm selection [ {answer} ] ?\n')
            if confirm == 'y':
                return answer
            else:
                time.sleep(.5)
                print('input new answer:')

def clearDisplay():
    '''
    Clears previous display
    '''
    os.system('cls' if os.name == 'nt' else 'clear')
