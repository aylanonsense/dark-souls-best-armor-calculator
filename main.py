import csv
import time

def parse_armor_list(filepath):
	records = csv_to_dict(filepath)
	for record in records:
		for int_attr in [ 'curse', 'phys', 'fire', 'light', 'thr', 'poison', 'sls', 'dark', 'str', 'mag', 'dur', 'petrify', 'bleed' ]:
			record[int_attr] = int(record[int_attr])
		for float_attr in [ 'weight', 'poise' ]:
			record[float_attr] = float(record[float_attr])
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
	for attr in ['curse', 'phys', 'fire', 'light', 'thr', 'poison', 'sls', 'dark', 'str', 'mag', 'dur', 'petrify', 'bleed', 'poise']:
		if armor_piece_1[attr] < armor_piece_2[attr]:
			return False
	#certain things are hard to compare, like effect, so when two weapons have different effects we can't call one strictly better
	if armor_piece_1['scaling'] != armor_piece_2['scaling'] or armor_piece_1['prerequisite'] != armor_piece_2['prerequisite'] or armor_piece_1['effect'] != armor_piece_2['effect']:
		return False
	#otherwise, yes, the first piece is strictly better than the second
	return True

#create scoring rubrics
scoring = [
	{
		'name': 'best-overall',
		'weights': { 'str': 1, 'sls': 1, 'thr': 1, 'mag': 1, 'fire': 1, 'light': 1, 'dark': 1, 'poise': 35 }
	}
]

#load armor data
#scaling, poise, curse, phys, name, weight, fire, light, thr, poison, sls, dark, effect, str, mag, reinforcement, dur, petrify, bleed, prerequisite
armor_lists = [
	parse_armor_list('head-armor.csv'),
	parse_armor_list('chest-armor.csv'),
	parse_armor_list('arm-armor.csv'),
	parse_armor_list('leg-armor.csv')
]

print "Num armor pieces: " + "/".join([str(len(x)) for x in armor_lists])

for l in range(0, len(armor_lists)):
	armor_piece_list = armor_lists[l]
	for i in range(0, len(armor_piece_list)):
		for j in range(i + 1, len(armor_piece_list)):
			if armor_piece_list[i] is not None and armor_piece_list[j] is not None:
				if is_strictly_better(armor_piece_list[i], armor_piece_list[j]):
					armor_piece_list[j] = None
				elif is_strictly_better(armor_piece_list[j], armor_piece_list[i]):
					armor_piece_list[i] = None
	armor_lists[l] = [x for x in armor_piece_list if x is not None]

print "Num armor pieces after removing \"strictly-betters\": " + "/".join([str(len(x)) for x in armor_lists])

for l in range(0, len(armor_lists)):
	armor_piece_list = armor_lists[l]
	for i in range(0, len(armor_piece_list)):
		if 'FTH' in armor_piece_list[i]['prerequisite'] or 'INT' in armor_piece_list[i]['prerequisite'] or 'Black Witch' in armor_piece_list[i]['name']:
			armor_piece_list[i] = None
	armor_lists[l] = [x for x in armor_piece_list if x is not None]

print "Num armor pieces after removing INT/FTH gear: " + "/".join([str(len(x)) for x in armor_lists])

#generate list of all possible armor sets
num_possible_armor_sets = product([len(x) for x in armor_lists])
milestones = [int(float(x) / 50 * num_possible_armor_sets) for x in range(1, 50)]

for rubric in scoring:
	max_weight = 0
	print "Grading based on " + rubric['name']

	print "  Scoring each individual piece of armor..."
	start_time = time.time()
	for armor_piece_list in armor_lists:
		for armor_piece in armor_piece_list:
			armor_piece['score'] = 0
			for attr in rubric['weights']:
				armor_piece['score'] += rubric['weights'][attr] * armor_piece[attr]
	end_time = time.time()
	print "  ... done scoring! (took %g seconds)" % (end_time - start_time)

	print "  Picking top armor sets for each weight range..."
	start_time = time.time()
	top_armor_sets_by_weight = {}
	for i in range(0, num_possible_armor_sets):
		if i in milestones:
			print str(100 * (i + 1) / num_possible_armor_sets) + " percent done"
		#generate a hypothetical armor set
		j = 1
		armor_pieces = []
		for armor_piece_list in armor_lists:
			if len(armor_piece_list) > 0:
				armor_pieces.append(armor_piece_list[(i / j) % len(armor_piece_list)])
				j *= len(armor_piece_list)
		armor_set = {
			'pieces': armor_pieces,
			'weight': sum([x['weight'] for x in armor_pieces])
		}
		#now do stuff with each armor set
		max_weight = max(max_weight, armor_set['weight'])
		armor_set['score'] = sum([x['score'] for x in armor_set['pieces']])
		armor_set_key = str(armor_set['weight'])
		if armor_set_key in top_armor_sets_by_weight:
			competing_armor_set = top_armor_sets_by_weight[armor_set_key]
			if competing_armor_set['score'] < armor_set['score']:
				top_armor_sets_by_weight[armor_set_key] = armor_set
		else:
			top_armor_sets_by_weight[armor_set_key] = armor_set
	end_time = time.time()
	print "  ... done picking top armor sets! (took %g seconds)" % (end_time - start_time)

	print "  Printing results..."
	start_time = time.time()
	prev_top_armor_set = None
	start_of_range = None
	for i in range(0, int(10 * max_weight)):
		weight = float(i) / 10
		weight_key = str(weight)
		if weight_key in top_armor_sets_by_weight:
			armor_set = top_armor_sets_by_weight[weight_key]
			if prev_top_armor_set is None:
				prev_top_armor_set = armor_set
				start_of_range = weight
			elif prev_top_armor_set['score'] < armor_set['score']:
				print str(start_of_range).rjust(5) + " to " + str(weight - 0.1).ljust(5) + (" (" + str(prev_top_armor_set['score']) + ")").ljust(12) + " ".join([x['name'].ljust(35) for x in prev_top_armor_set['pieces']])
				start_of_range = weight
				prev_top_armor_set = armor_set
	if prev_top_armor_set:
		print str(start_of_range).rjust(5) + "+        " + (" (" + str(prev_top_armor_set['score']) + ")").ljust(12) + " ".join([x['name'].ljust(35) for x in prev_top_armor_set['pieces']])
	end_time = time.time()
	print "  ... done printing results! (took %g seconds)" % (end_time - start_time)

