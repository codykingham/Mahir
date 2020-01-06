'''
Tools for maintaining and editing Mahir vocab jsons
'''

import json
from datetime import datetime

def save(data, file):
    '''
    Saves a json vocab file with proper indentation 
    and ensure_ascii=False
    '''
    with open(file, 'w') as outfile:
        json.dump(data, outfile, indent=1, ensure_ascii=False)
        
def deleteterm(setdata, termid):
    '''
    Deletes a term from an entire set.
    ! Do not use on same dict as iteration ! 
    '''
    score = setdata['terms_dict'][termid]['score']
    del setdata['terms_dict'][termid]
    setdata['term_queues'][score].remove(termid)

def reindex(vocdat):
    '''
    Given a vocab set dict,
    reindexes all term ids back
    from 1 to N.
    '''
    newterms = {}
    newqueues = {}
    old2newid = {}
    maxID = 1
    
    # make the new termsdict and mapping 
    for vid, vdata in vocdat['terms_dict'].items():

        # configure new metadata
        newID = str(maxID)
        newterms[newID] = {k:v for k,v in vdata.items()}

        # map old termID to new
        old2newid[vid] = newID

        # iterate new node number up one
        maxID += 1
    
    # make new term queues
    for score, queue in vocdat['term_queues'].items():
        new_queue = [old2newid[tid] for tid in queue]
        newqueues[score] = new_queue
        
    # Affect the changes
    vocdat['terms_dict'] = newterms
    vocdat['term_queues'] = newqueues
    
    return vocdat

def merge(vocdat, ids):
    '''
    Given a vocab set dict and a list of ids,
    merges all ids to the leftmost id.
    '''
    
    # leftmost id subsumes others
    target = vocdat['terms_dict'][ids[0]]
    
    # subsume right into left; delete right
    for tid in ids[1:]:
        origin = vocdat['terms_dict'][tid]
        target['source_lexemes'].extend(origin['source_lexemes'])
        target['gloss'] += '; '+origin['gloss']
        target['term'] += '; '+origin['term']
        deleteterm(vocdat, tid)
        
    return vocdat

def blank(vocdat):
    '''
    Prepares a fresh version of a vocab set
    '''
    new_vocdat = {
        'name': vocdat['name'],
        'init_date': str(datetime.now()),
        'description': vocdat['description'],
        'app_data': vocdat['app_data'],
        'cycle_data': vocdat['cycle_data'],
        'scoreconfig': vocdat['scoreconfig'],
        'term_queues': {
            score:[] for score in vocdat['term_queues']
        },
        'terms_dict': vocdat['terms_dict'],
        'stats': [],
    }
    
    # set score 0 queue
    new_vocdat['term_queues']['0'] = [
        id for id in new_vocdat['terms_dict']
    ]

    # zero out and configure cycle_data
    new_vocdat['cycle_data']['ncycle'] = 0
    new_vocdat['cycle_data']['total_sessions'] = 0
    new_vocdat['cycle_data']['score_starts'] = {
        score:len(queue) for score, queue in new_vocdat['term_queues'].items()
    }

    # reset individual term stats
    for term, tdat in new_vocdat['terms_dict'].items():
        tdat['stats'] = {'seen':0,'missed':0}

    return new_vocdat
