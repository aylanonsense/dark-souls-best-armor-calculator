import csv
import time

def parse_armor_piece_list(filepath):
	records = csv_to_dict(filepath)
	for record in records:
		for i in ['physical', 'strike', 'slash', 'thrust', 'magic', 'fire', 'lightning', 'dark', 'poison', 'bleed', 'petrify', 'curse', 'durability']:
			record[i] = int(record[i])
		for i in ['weight', 'poise']:
			record[i] = float(record[i])
		if record['set'] == '':
			record['set'] = None
	return records

def csv_to_dict(filepath):
	datafile = open(filepath, 'r')
	datareader = csv.reader(datafile)
	records = []
	headers = None
	for row in datareader:
		if headers is None:
			headers = row
		else:
			record = {}
			for i in range(0, len(headers)):
				record[headers[i].lower()] = row[i]
			records.append(record)
	return records

def product(list):
    p = 1
    for i in list:
        p *= i
    return p

def is_strictly_better(armor_piece_1, armor_piece_2):
	#if the first armor piece is heavier than the second, the first can't be strictly better
	if armor_piece_1['weight'] > armor_piece_2['weight']:
		return False
	#if any attribute of the second is greater than the first, the first can't be strictly better
	for attr in ['physical', 'strike', 'slash', 'thrust', 'magic', 'fire', 'lightning', 'dark', 'poison', 'bleed', 'petrify', 'curse', 'durability']:
		if armor_piece_1[attr] < armor_piece_2[attr]:
			return False
	#certain things are hard to compare, like effect, so when two weapons have different effects we can't call one strictly better
	if armor_piece_1['scaling'] != armor_piece_2['scaling'] or armor_piece_1['prerequisite'] != armor_piece_2['prerequisite'] or armor_piece_1['effect'] != armor_piece_2['effect']:
		return False
	#otherwise, yes, the first piece is strictly better than the second
	return True

def create_linear_scoring_function(weights):
	def score_armor_set(armor_pieces):
		score = 0
		for attr in weights:
			total_attr = 0
			for armor_piece in armor_pieces:
				total_attr += armor_piece[attr]
			score += total_attr * weights[attr]
		return score
	return score_armor_set


#create scoring rubrics
rubrics = [
	{'name': "Best Overall", 'scoring_func': create_linear_scoring_function({'poise': 12.0, 'physical': 1.5, 'strike': 1, 'slash': 1, 'thrust': 1, 'magic': 1, 'fire': 1, 'lightning': 1, 'dark': 1, 'poison': 0.3, 'bleed': 0.1, 'petrify': 0.05, 'curse': 0.05})},
	{'name': "Poise", 'scoring_func': create_linear_scoring_function({'poise': 1.0})},
	{'name': "Total Defense", 'scoring_func': create_linear_scoring_function({'physical': 1.0,'strike': 1.0,'slash': 1.0,'thrust': 1.0,'magic': 1.0,'fire': 1.0,'lightning': 1.0,'dark': 1.0})},
	{'name': "Total Defense and Resistances", 'scoring_func': create_linear_scoring_function({'physical': 1.0, 'strike': 1.0, 'slash': 1.0, 'thrust': 1.0, 'magic': 1.0, 'fire': 1.0, 'lightning': 1.0, 'dark': 1.0, 'poison': 1.0, 'bleed': 1.0, 'petrify': 1.0, 'curse': 1.0})},
	{'name': "Physical Defense", 'scoring_func': create_linear_scoring_function({'physical': 1.0, 'strike': 1.0, 'slash': 1.0, 'thrust': 1.0})},
	{'name': "Magic Defense", 'scoring_func': create_linear_scoring_function({'magic': 1.0})},
	{'name': "Fire Defense", 'scoring_func': create_linear_scoring_function({'fire': 1.0})},
	{'name': "Lightning Defense", 'scoring_func': create_linear_scoring_function({'lightning': 1.0})},
	{'name': "Dark Defense", 'scoring_func': create_linear_scoring_function({'dark': 1.0})}
]
top_armor_sets = {}
for rubric in rubrics:
	top_armor_sets[rubric['name']] = {}

#load armor lists
armor_lists = [
	parse_armor_piece_list('head-armor.csv'),
	parse_armor_piece_list('chest-armor.csv'),
	parse_armor_piece_list('arm-armor.csv'),
	parse_armor_piece_list('leg-armor.csv')
]
print("Loaded %s armor pieces" % "/".join([str(len(x)) for x in armor_lists]))

#remove unupgraded armor
for l in range(0, len(armor_lists)):
	armor_lists[l] = [x for x in armor_lists[l] if '+' in x['name']]
print("Looking at %s upgraded armor pieces" % "/".join([str(len(x)) for x in armor_lists]))

#debug -- limit the list to make it run a bunch faster
# for l in range(0, len(armor_lists)):
# 	armor_lists[l] = armor_lists[l][:12]
# print("Culled list down to %s armor pieces (debug mode)" % "/".join([str(len(x)) for x in armor_lists]))

#find full armor sets
preconstructed_armor_sets = {}
for armor_piece_list in armor_lists:
	for armor_piece in armor_piece_list:
		if armor_piece['set'] is not None:
			if armor_piece['set'] not in preconstructed_armor_sets:
				preconstructed_armor_sets[armor_piece['set']] = []
			preconstructed_armor_sets[armor_piece['set']].append(armor_piece)
print("Found %i armor sets (%i of which have four pieces)" % (len(preconstructed_armor_sets), len([x for x in preconstructed_armor_sets if len(preconstructed_armor_sets[x]) == 4])))

#crunch numbers and determine ranges
num_possible_armor_sets = product([len(x) for x in armor_lists])
min_armor_set_weight = sum(min([y['weight'] for y in x]) for x in armor_lists)
max_armor_set_weight = sum(max([y['weight'] for y in x]) for x in armor_lists)
print("Evaluating %i possible mix-and-matched armor sets between %g and %g lbs" % (num_possible_armor_sets, min_armor_set_weight, max_armor_set_weight))

#evaluate every possible mix-and-matched armor set
start_time = time.time()
time_of_last_print = start_time
k = 0
for i in range(0, num_possible_armor_sets):
	j = 1
	armor_pieces = []
	for armor_piece_list in armor_lists:
		if len(armor_piece_list) > 0:
			armor_pieces.append(armor_piece_list[(i / j) % len(armor_piece_list)])
			j *= len(armor_piece_list)
	weight = sum(x['weight'] for x in armor_pieces)
	weight_key = str(int(10 * weight))
	for rubric in rubrics:
		score = rubric['scoring_func'](armor_pieces)
		if weight_key not in top_armor_sets[rubric['name']] or top_armor_sets[rubric['name']][weight_key]['score'] < score:
			top_armor_sets[rubric['name']][weight_key] = {'pieces': armor_pieces, 'score': score}
	if i % 10000 == 0:
		now = time.time()
		if now - time_of_last_print >= 10:
			print "%i armor sets evaluated (%f%%)" % (i - k, (100.0 * i) / num_possible_armor_sets)
			k = i
			time_of_last_print = now
end_time = time.time()
print("Done evaluating! (took %g seconds)" % (end_time - start_time))

#print the best of each category
for rubric in rubrics:
	print("\nResults for %s:" % rubric['name'])
	print("  Weight   Score   Pieces")
	prev_armor_set = None
	start_of_range = None
	for i in range(int(10 * min_armor_set_weight), int(10 * max_armor_set_weight)):
		weight = i / 10.0
		weight_key = str(i)
		if weight_key in top_armor_sets[rubric['name']]:
			if prev_armor_set is None or prev_armor_set['score'] < top_armor_sets[rubric['name']][weight_key]['score']:
				if prev_armor_set is not None:
					print(" %s-%s %s %s" % (str(start_of_range).rjust(4), str(weight - 0.1).ljust(4), str(prev_armor_set['score']).ljust(7), " ".join([x['name'].ljust(30) for x in prev_armor_set['pieces']])))
				prev_armor_set = top_armor_sets[rubric['name']][weight_key]
				start_of_range = weight
	if prev_armor_set is not None:
		print(" %s+     %s %s" % (str(start_of_range).rjust(4), str(prev_armor_set['score']).ljust(7), " ".join([x['name'].ljust(30) for x in prev_armor_set['pieces']])))
	print("\n Comparison to armor sets:")
	print("    Weight Score   Set                  Extra Weight  Foregone Score")
	for armor_set_name in preconstructed_armor_sets:
		armor_set = preconstructed_armor_sets[armor_set_name]
		if len(armor_set) == 4:
			better_armor_set = None
			lighter_armor_set = None
			weight = sum([x['weight'] for x in armor_set])
			score = rubric['scoring_func'](armor_set)
			other_weight = weight
			while other_weight >= min_armor_set_weight:
				other_weight_key = str(int(10 * other_weight))
				if other_weight_key in top_armor_sets[rubric['name']]:
					other_armor_set = top_armor_sets[rubric['name']][other_weight_key]
					if other_armor_set['score'] >= score:
						if better_armor_set is None or other_armor_set['score'] >= better_armor_set['score']:
							better_armor_set = other_armor_set
						lighter_armor_set = other_armor_set
				other_weight -= 0.1
			extra_weight = weight - sum([x['weight'] for x in lighter_armor_set['pieces']]) if lighter_armor_set is not None else 0.0
			foregone_score = better_armor_set['score'] - score if better_armor_set is not None else 0.0
			print("    %s   %s %s %s %i" % (str(weight).ljust(4), str(score).ljust(7), armor_set[0]['set'].ljust(20), str(extra_weight).ljust(13),	foregone_score))