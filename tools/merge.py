'''
This module reindexes a Mahir study set from 1 to N. 
This is necessary when terms are deleted or merged and
the IDs have gaps.
'''

import sys
import json
from tools import reindex, merge, save

try: 
    file = sys.argv[1]
except:
    print('no file given...doing nothing...')
    
# get ids to merge
tomerge = sys.argv[2:]

# load the vocab file
with open(file, 'r') as infile:
    vocab = json.load(infile)
    
# merge requested term ids
merged = merge(vocab, tomerge)
    
# reindex term ids from 1 to N
reindexed = reindex(vocab)

# export data back to file
save(reindexed, file)