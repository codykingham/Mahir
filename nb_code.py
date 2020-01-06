# import modules
import os, json
from pprint import pprint
import collections
from datetime import datetime
from IPython.display import display
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from iMahir import loadStudy

def plot_progress(heb):
    """Make a plot of learned/unlearned terms"""
    
    sessions = [sd for sd in heb.set_data['stats'] if 'score_counts' in sd]
    learned_lengths = [sum(s['score_counts'][scr] for scr in s['score_counts'] if int(scr) > 2) 
                           for s in sessions]
    unlearned_lengths = [s['score_counts']['0'] for s in sessions]
    dates = [datetime.strptime(sd['date'], '%Y-%m-%d %H:%M:%S.%f') for sd in sessions]
    date_labels = [datetime.strftime(time, format='%d-%m_%H:%M') for time in dates]
    date2nlearned = dict(zip(date_labels, learned_lengths)) # get dict for references
    date2nunlearned = dict(zip(date_labels, unlearned_lengths))

    # plot this data only with cutoff
    cutoff = -30 # max amount
    plt_sessions = sessions[cutoff:]
    plt_learned = learned_lengths[cutoff:]
    plt_unlearned = unlearned_lengths[cutoff:]
    plt_dates = date_labels[cutoff:]

    # calculate cycle lines
    cycle_bounds = []
    last_cycle = None
    for i, sd in enumerate(plt_sessions):
        cycle = sd['cycle']
        last_cycle = cycle if not last_cycle else last_cycle
        if last_cycle != cycle:
            cycle_bounds.append(i-0.5)
            last_cycle = cycle
            
    # make the plot
    x = np.arange(len(plt_learned))
    plt.figure(figsize=(13, 7))
    plt.plot(x, plt_learned, linestyle='dotted', color='lightblue')
    plt.scatter(x, plt_learned, color='darkblue')
    plt.plot(x, plt_unlearned, linestyle='dotted', color='pink')
    plt.scatter(x, plt_unlearned, color='darkred')
    plt.xticks(x, plt_dates, rotation=90, size=10)
    plt.yticks(size=12)
    plt.ylabel('# of Terms', size=16)
    plt.xlabel('Study Session Date', size=16)
    plt.title(f'learned: {plt_learned[-1]}\nunlearned {plt_unlearned[-1]}', size=16)
    for bound in cycle_bounds:
        plt.axvline(bound, color='grey', linestyle='dotted')
    plt.show()
    
    last_transition = plt_dates[int(cycle_bounds[-1] - 0.5)] # get date of last cycle switch
    print('n-learned since last cycle:', plt_learned[-1] - date2nlearned[last_transition])

def plot_freqs(heb):
    # get terms left to learn
    to_learn = collections.Counter()
    for i in heb.set_data['term_queues']['0']:
        term_lexs = heb.set_data['terms_dict'][i]['source_lexemes']
        for term in term_lexs:
            freq = heb.F.freq_lex.v(term)
            to_learn[freq] += 1           
    to_learn = pd.DataFrame.from_dict(to_learn, orient='index').sort_values(by=0)

    # make the plot
    nbars = np.arange(to_learn.shape[0])
    plt.figure(figsize=(10, 6))
    sns.barplot(nbars, to_learn[0], color='darkred')
    plt.xticks(nbars, labels=list(str(i) for i in to_learn.index), size=12)
    plt.yticks(size=12)
    plt.ylabel('N-Terms', size=16)
    plt.xlabel('Freq', size=16)
    plt.title(f'remaining frequencies', size=16)
    plt.show()
    display(to_learn)