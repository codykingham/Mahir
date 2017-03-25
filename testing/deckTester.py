from ManageSets import buildDeck
import pickle, collections, json
from pprint import pprint

with open('term_queues.pickle','rb') as infile:
	term_queues = pickle.load(infile)

with open('test_set.json') as infile:
	term_dict = json.load(infile)

# num of simulated cycles
sim_cycles = 60

# holds the term queues/decks throughout the simulated study cycle
queues = None
decks = []

# run the cycle
for i in range(1,sim_cycles):

	# initialize new deck at start
	if not queues:
		initial_deck = buildDeck(term_queues)
		queues = initial_deck[1]
		decks.append(initial_deck[0])

	session = buildDeck(queues)
	queues = session[1]
	decks.append(session[0])

# Measure the results
# We test the average occurrence of a term with a particular score

test = collections.defaultdict(lambda: collections.Counter())
for deck in decks:
	for term in deck['terms']:
		score = term_dict[term]['score']
		test[score].update([term])

# gather occurrence counts (i.e. the number of occurrences of a term, gathered into a list, corresponded with its score)
occurrence_count = collections.defaultdict(list)
for score, term_counts in test.items():
	for term, count in term_counts.items():
		occurrence_count[score].append(count)

# print report
print('\n\t\t~~ MAHIR DECK SIMULATION ~~')

print(f'sim sessions: {sim_cycles}')
print(f"deck size: {len(decks[0]['terms'])}")

print('\n')

# present the averages
for score, occ_count in sorted(occurrence_count.items()):
	term_amount = len(test[score])
	total_counts = sum(occurrence_count[score])
	average = round(total_counts / term_amount, 2)

	print(f'score: {score}')
	print(f'average: {average}')
	print(f'# terms: {term_amount}')
	print(f'term occurrences: {total_counts}')
	print()
