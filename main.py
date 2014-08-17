import csv

def parse_armor(filepath):
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

#load armor data
#scaling, poise, curse, phys, name, weight, fire, light, thr, poison, sls, dark, effect, str, mag, reinforcement, dur, petrify, bleed, prerequisite
head_armor_list = parse_armor('head-armor.csv')
chest_armor_list = parse_armor('chest-armor.csv')
arm_armor_list = parse_armor('arm-armor.csv')
leg_armor_list = parse_armor('leg-armor.csv')

#create scoring rubrics
scoring = [
	{
		'name': 'highest-poise',
		'weights': { 'poise': 1 }
	},
	{
		'name': 'highest-defense',
		'weights': { 'str': 1, 'sls': 1, 'thr': 1, 'mag': 1, 'fire': 1, 'light': 1, 'dark': 1 }
	},
	{
		'name': 'best-overall',
		'weights': { 'str': 1, 'sls': 1, 'thr': 1, 'mag': 1, 'fire': 1, 'light': 1, 'dark': 1, 'poise': 15 }
	}
]

#limit lists for debugging purposes (so it doesn't take forever)
head_armor_list = head_armor_list[0:10]
chest_armor_list = chest_armor_list[0:10]
arm_armor_list = arm_armor_list[0:10]
leg_armor_list = leg_armor_list[0:10]

#for each scoring rubric
for rubric in scoring:
	print "Grading based on " + rubric['name']
	#for each potential combination of armor
	top_armor_sets_by_weight = {}
	max_weight = 0
	for helm in head_armor_list:
		for chest_piece in chest_armor_list:
			for gauntlet in arm_armor_list:
				for leggings in leg_armor_list:
					armor_set_pieces = [ helm, chest_piece, gauntlet, leggings ]
					armor_set_weight = sum([ x['weight'] for x in armor_set_pieces ])
					max_weight = max(max_weight, armor_set_weight)
					armor_set_score = 0
					for armor_piece in armor_set_pieces:
						for attr in rubric['weights']:
							armor_set_score += rubric['weights'][attr] * armor_piece[attr]
					if armor_set_weight in top_armor_sets_by_weight:
						competing_armor_set = top_armor_sets_by_weight[str(armor_set_weight)]
						if competing_armor_set['score'] < armor_set_pieces['score']:
							top_armor_sets_by_weight[str(armor_set_weight)] = { 'score': armor_set_score, 'pieces': armor_set_pieces }
					else:
						top_armor_sets_by_weight[str(armor_set_weight)] = { 'score': armor_set_score, 'pieces': armor_set_pieces }


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
				print str(start_of_range).rjust(5) + " to " + str(weight - 0.1).ljust(5) + (" (" + str(prev_top_armor_set['score']) + ")").ljust(12) + " ".join([x['name'].ljust(30) for x in prev_top_armor_set['pieces']])
				start_of_range = weight
				prev_top_armor_set = armor_set
	if prev_top_armor_set:
		print str(start_of_range).rjust(5) + "+        " + (" (" + str(prev_top_armor_set['score']) + ")").ljust(12) + " ".join([x['name'].ljust(30) for x in prev_top_armor_set['pieces']])

