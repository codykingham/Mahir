import sys
import json
from tools import blank

try: 
    file = sys.argv[1]
    output = sys.argv[2]
except:
    print('no file given...doing nothing...')
    
# load the vocab file
with open(file, 'r') as infile:
    vocab = json.load(infile)