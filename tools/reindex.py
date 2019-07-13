'''
This module reindexes a Mahir study set from 1 to N. 
This is necessary when terms are deleted or merged and
the IDs have gaps.
'''

import sys
import json
from tools import reindex
from tools import save

try: 
    file = sys.argv[1]
except:
    print('no file given...doing nothing...')

# load the vocab file
with open(file, 'r') as infile:
    vocab = json.load(infile)
    
# reindex data
reindexed = reindex(vocab)

# export data back to file
save(reindexed, file)