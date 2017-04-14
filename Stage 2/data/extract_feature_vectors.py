# -*- coding: utf-8 -*-
# @Author: charlotte
# @Date:   2017-02-12 17:32:35
# @Last Modified by:   charlotte
# @Last Modified time: 2017-02-28 18:47:05

# cd ../data/; python extract_feature_vectors.py -l=-1 -u=600 -r=randomized; cd ../ml_package/

from __future__ import print_function
import argparse
import re
import os
import codecs
import collections
import random
import fuzzy
import sys
import warnings
from math import floor

suffix_blacklist = ['ese', 'can', 'ian', 'ric', 'ish', 'man']
suffix_whitelist = ['polis', 'ville', 'ford', 'furt', 'forth', 'shire', 'boro', 'borough', 'field', 'bridge', 'chester', 'mouth', 'town', 'ton', 'land', 'yard']
preposition_list = ['with', 'at', 'from', 'into', 'of', 'to', 'in', 'for', 'on', 'by', 'between', 'near', 'under', 'above', 'towards']
followed_by_list = ['where', 'that', 'which', 'when', 'whose', 'whom']
followed_by_list += ['is', 'are', 'was', 'were', 'has', 'have', 'had']
soundex = fuzzy.Soundex(4)
string_hash_seed = 0.1
normalize_vector_constant = {'soundex': (-20000, 26000), 'name': (0, 1000), 'pre_word_1': (0, 500), 'pre_word_3': (0, 500), 'pre_word_2': (0, 500), 'trail_word_2': (0, 500), 'trail_word_3': (0, 500), 'trail_word_1': (0, 500)}
normalize_scale_factor = 10.0

# Compute the start and end position for words in article
def compute_word_position(in_file):
	word_position = []
	with open(in_file) as file:
		re_words = re.compile(r'[^(\’\:\“\,\—\.\”\-\"\?\')^\s]+', re.UNICODE)
		for match in re.finditer(re_words, file.read()):
			name = re.sub(r'<place>|</place>', '', match.group())
			word_position += [{'name':name, 'start':match.start(), 'end':match.end()}]
	# for s in word_position:
	# 	print('{}, {}'.format(s['start'], s['name']))
	return word_position

# Compute the start and end position of labeled words
def compute_labeled_position(in_file, word_position):
	labeled_position = []
	with open(in_file) as file:
		re_tags = re.compile(r'<place>(.*?)</place>')
		for match in re.finditer(re_tags, file.read()):
			# print(match.group())
			start_offset = word_offset_start(match.start(), word_position)
			end_offset = word_offset_end(match.end(), word_position)
			labeled_position += [{'name':match.group(), 'start':start_offset, 'end':end_offset, 'file':in_file}]
	return labeled_position

# Compute the start and end position of unlabeled words
def compute_unlabeled_position(labeled_position, word_position, max_span=3):
	# Stores positions of negative examples
	unlabeled_matrix = [[i for i in range(len(word_position))] for j in range(max_span)]
	for span in range(max_span):
		for labeled in labeled_position:
			# Remove everything that belongs to a lebeled word
			for i in range(labeled['start'], labeled['end']+1):
				try:
					unlabeled_matrix[span].remove(i)
				except Exception as e:
					pass
			for i in range(1, span+1):
				# Remove words preceding a labeled word to make room for word span
				try:
					pos = labeled['start'] - i
					unlabeled_matrix[span].remove(pos)
				except Exception as e:
					pass
				# Remove words at the end to avoid exception
				try:
					pos = len(word_position) - i
					unlabeled_matrix[span].remove(pos)
				except Exception as e:
					pass
	# Stores the vector for negative examples (name, start, end)
	unlabeled_position = []
	for span in range(max_span):
		for pos in unlabeled_matrix[span]:
			# print(pos)
			for i in range(pos, pos+span+1):
				try:
					name = ' '.join([word_position[i]['name']])
					start = pos
					end = pos + span
					unlabeled_position += [{'name':name, 'start':start, 'end':end,'file':in_file}]
				except Exception as e:
					pass
	return unlabeled_position

# Phase two: for each located words, generate the feature vector
def compute_feature_vector(word_position, labeled_position, normalize_vector, num=-1):
	feature_vector = []
	num = len(labeled_position) if num == -1 else min(len(labeled_position), num)
	for i in range(num):
		p = labeled_position[i]
		################ Attributes ################
		name = p['name']
		# print(name)
		is_target = 0
		if name.startswith('<place>'):
			name = name[7:]
			is_target = 1
		if name.endswith('</place>'):
			name = name[:-8]
			is_target = 1
		start = p['start']
		end = p['end']
		new_vector = collections.OrderedDict()
		name_h = string_hash(name)
		new_vector.update({'is_target': is_target, 'name': name_h})
		if not 'name' in normalize_vector:
			normalize_vector['name'] = (name_h, name_h)
		elif name_h < normalize_vector['name'][0]:
			old_record = normalize_vector['name']
			normalize_vector['name'] = (name_h, old_record[1])
		elif name_h > normalize_vector['name'][1]:
			old_record = normalize_vector['name']
			normalize_vector['name'] = (old_record[0], name_h)

		################ The preceding words ################
		pre_word_1 = None
		if start > 0:
			pre_word_1 = word_position[start-1]['name'].lower()
		pre_word_2 = None
		if start > 1:
			pre_word_2 = word_position[start-2]['name'].lower()
		pre_word_3 = None
		if start > 2:
			pre_word_3 = word_position[start-3]['name'].lower()
		pre_word_1_h = string_hash(pre_word_1)
		pre_word_2_h = string_hash(pre_word_2)
		pre_word_3_h = string_hash(pre_word_3)
		new_vector.update({'pre_word_1':pre_word_1_h, 'pre_word_2':pre_word_2_h, 'pre_word_3':pre_word_3_h})
		if not 'pre_word_1' in normalize_vector:
			normalize_vector['pre_word_1'] = (pre_word_1_h, pre_word_1_h)
		elif pre_word_1_h < normalize_vector['pre_word_1'][0]:
			old_record = normalize_vector['pre_word_1']
			normalize_vector['pre_word_1'] = (pre_word_1_h, old_record[1])
		elif pre_word_1_h > normalize_vector['pre_word_1'][1]:
			old_record = normalize_vector['pre_word_1']
			normalize_vector['pre_word_1'] = (old_record[0], pre_word_1_h)
		if not 'pre_word_2' in normalize_vector:
			normalize_vector['pre_word_2'] = (pre_word_2_h, pre_word_2_h)
		elif pre_word_2_h < normalize_vector['pre_word_2'][0]:
			old_record = normalize_vector['pre_word_2']
			normalize_vector['pre_word_2'] = (pre_word_2_h, old_record[1])
		elif pre_word_2_h > normalize_vector['pre_word_2'][1]:
			old_record = normalize_vector['pre_word_2']
			normalize_vector['pre_word_2'] = (old_record[0], pre_word_2_h)
		if not 'pre_word_3' in normalize_vector:
			normalize_vector['pre_word_3'] = (pre_word_3_h, pre_word_3_h)
		elif pre_word_3_h < normalize_vector['pre_word_3'][0]:
			old_record = normalize_vector['pre_word_3']
			normalize_vector['pre_word_3'] = (pre_word_3_h, old_record[1])
		elif pre_word_3_h > normalize_vector['pre_word_3'][1]:
			old_record = normalize_vector['pre_word_3']
			normalize_vector['pre_word_3'] = (old_record[0], pre_word_3_h)

		################ The following words ################
		trail_word_1 = None
		if end < len(word_position)-1:
			trail_word_1 = word_position[end+1]['name'].lower()
		trail_word_2 = None
		if end < len(word_position)-2:
			trail_word_2 = word_position[end+2]['name'].lower()
		trail_word_3 = None
		if end < len(word_position)-3:
			trail_word_3 = word_position[end+3]['name'].lower()
		trail_word_1_h = string_hash(trail_word_1)
		trail_word_2_h = string_hash(trail_word_2)
		trail_word_3_h = string_hash(trail_word_3)
		new_vector.update({'trail_word_1':trail_word_1_h, 'trail_word_2':trail_word_2_h, 'trail_word_3':trail_word_3_h})
		if not 'trail_word_1' in normalize_vector:
			normalize_vector['trail_word_1'] = (trail_word_1_h, trail_word_1_h)
		elif trail_word_1_h < normalize_vector['trail_word_1'][0]:
			old_record = normalize_vector['trail_word_1']
			normalize_vector['trail_word_1'] = (trail_word_1_h, old_record[1])
		elif trail_word_1_h > normalize_vector['trail_word_1'][1]:
			old_record = normalize_vector['trail_word_1']
			normalize_vector['trail_word_1'] = (old_record[0], trail_word_1_h)
		if not 'trail_word_2' in normalize_vector:
			normalize_vector['trail_word_2'] = (trail_word_2_h, trail_word_2_h)
		elif trail_word_2_h < normalize_vector['trail_word_2'][0]:
			old_record = normalize_vector['trail_word_2']
			normalize_vector['trail_word_2'] = (trail_word_2_h, old_record[1])
		elif trail_word_2_h > normalize_vector['trail_word_2'][1]:
			old_record = normalize_vector['trail_word_2']
			normalize_vector['trail_word_2'] = (old_record[0], trail_word_2_h)
		if not 'trail_word_3' in normalize_vector:
			normalize_vector['trail_word_3'] = (trail_word_3_h, trail_word_3_h)
		elif trail_word_3_h < normalize_vector['trail_word_3'][0]:
			old_record = normalize_vector['trail_word_3']
			normalize_vector['trail_word_3'] = (trail_word_3_h, old_record[1])
		elif trail_word_3_h > normalize_vector['trail_word_3'][1]:
			old_record = normalize_vector['trail_word_3']
			normalize_vector['trail_word_3'] = (old_record[0], trail_word_3_h)

		################ Length ################
		length = len(name)
		new_vector.update({'length': length})

		################ All capitalized ################
		all_capitalized = 1
		for w in re.finditer(r'[^\s]+', name):
			if w.group()[0].islower():
				all_capitalized = 0
				break
		new_vector.update({'all_capitalized': all_capitalized})

		################ Suffix black/white lists ################
		suffix_blacklisted = 0
		for s in suffix_blacklist:
			if name.endswith(s):
				suffix_blacklisted = 1
				break
		suffix_whilelisted = 0
		for s in suffix_whitelist:
			if name.endswith(s):
				suffix_whilelisted = 1
				break
		new_vector.update({'suffix_blacklisted': suffix_blacklisted})
		new_vector.update({'suffix_whilelisted': suffix_whilelisted})

		################ Preceding prepositon ################
		preposition_dict = {}
		for s in preposition_list:
			if pre_word_1 == s:
				preposition_dict[s] = 1
			else:
				preposition_dict[s] = 0
		new_vector.update(preposition_dict)

		################ Followed by ################
		followed_by_dict = {}
		for s in followed_by_list:
			if trail_word_1 == s:
				followed_by_dict[s] = 1
			else:
				followed_by_dict[s] = 0
		new_vector.update(followed_by_dict)

		################ Phonetic analysis ################
		sd = soundex(name)
		soundex_h = soundex_hash(sd)
		new_vector.update({'soundex':soundex_h})
		if not 'soundex' in normalize_vector:
			normalize_vector['soundex'] = (soundex_h, soundex_h)
		elif soundex_h < normalize_vector['soundex'][0]:
			old_record = normalize_vector['soundex']
			normalize_vector['soundex'] = (soundex_h, old_record[1])
		elif soundex_h > normalize_vector['soundex'][1]:
			old_record = normalize_vector['soundex']
			normalize_vector['soundex'] = (old_record[0], soundex_h)

		feature_vector += [new_vector]

	return feature_vector

# Classify negative examples
def filter_negtive_example(negative_feature_vector, total_len = 1000, cap_percent = 0.5):
	# select all capitalized elements
	capitalized_list = []
	not_capitalized_list = []
	for u in negative_feature_vector:
		if u['all_capitalized'] == 1:
			capitalized_list += [u]
			# print(u['name'])
		else:
			not_capitalized_list += [u]

	# calculate number of selected element to keep
	num_capitalized = int(floor(total_len * cap_percent))
	if num_capitalized > len(capitalized_list):
		num_capitalized = len(capitalized_list)
		print('There is no enough capatalized negative examples, using the size {}'.format(num_capitalized))
	num_not_captalized = total_len - num_capitalized
	if num_not_captalized > len(not_capitalized_list):
		num_not_captalized = len(not_capitalized_list)
		print('There is no enough uncapatalized negative examples, using the size {}'.format(num_not_captalized))

	# randomly choose from the list
	filtered_list = []
	rand_index = random.sample(range(len(capitalized_list)), num_capitalized)
	for r in rand_index:
		filtered_list += [capitalized_list[r]]
	rand_index = random.sample(range(len(not_capitalized_list)), num_not_captalized)
	for r in rand_index:
		filtered_list += [not_capitalized_list[r]]	

	return filtered_list


# Return the word offset of labeled words
def word_offset_start(labeled_position, word_position):
	for i in range(0, len(word_position)):
		if labeled_position < word_position[i]['start']:
			return i-1
		if labeled_position == word_position[i]['start']:
			return i
	# word position out of bound
	print('Error: word position out of bound')
	raise Exception

# Return the word offset of labeled words
def word_offset_end(labeled_position, word_position):
	for i in reversed(range(0, len(word_position))):
		if labeled_position >= word_position[i]['end']:
			return i
	# word position out of bound
	print('Error: word position out of bound')
	raise Exception

# hash a string to double
def string_hash(string):
	if not string:
		return 0
	res = 0
	for i in range(len(string)):
		res += string_hash_seed * (i + 1) * ord(string[i])
	return res

# hash a soundex to double
def soundex_hash(string):
	if not string:
		return 0
	res = str(ord(string[0]) - ord('A'))
	res = res + string[1:]
	return int(res)

if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(description='Extracts feature vectors to use as input to ML classifier')
	parser.add_argument('-f', '--filename', type=str, help='Enter the output file name')
	parser.add_argument('-d', '--debug', type=str, help='Enter the debug output file name')
	parser.add_argument('-l', '--labeled', type=int, help='Number of positive vectors to generate (-1 for all, default=all)')
	parser.add_argument('-u', '--unlabeled', type=int, help='Number of negative vectors to generate (-1 for all, default=all)')
	parser.add_argument('-p', '--percent', type=float, help='Percentage of all capitalized negative examples (default=0.5)')
	parser.add_argument('-r', '--random', type=str, help='Number of negative vectors to generate (ordered or randomized)')
	parser.add_argument('-m', '--multiplier', type=float, help='The number of negative examples divided by that of positive ones (default=3.0)')
	args = parser.parse_args()
	labeled_num = args.labeled if args.labeled != None else -1
	unlabeled_num = args.unlabeled if args.unlabeled != None else -1
	filtering_type = args.random if args.random != None else 'randomized'
	percent_all_capitalized = args.percent if args.percent != None else 0.5
	multiplier = args.multiplier if args.multiplier != None else 3

	use_multiplier = True
	if args.unlabeled and args.multiplier:
		print('--multiplier argument overrides --unlabeled')
	elif args.unlabeled:
		print('Using fixed number of negative examples')
		use_multiplier = False

	# Output filename
	out_file = args.filename if args.filename else 'feature_vectors.txt'
	# Error output redirect
	if args.debug:
		sys.stdout = open(args.debug, 'w+')
		sys.stderr = open(args.debug, 'w+')

	# Directories that will be considered
	directory_list = ['devl_set', 'test_set']

	for directory in directory_list:
		# Walk through all files in the directory
		positive_feature_vector = []
		negative_feature_vector = []
		normalize_vector = {}
		title_written = False
		filename = directory + '_' + out_file

		files = os.listdir(os.path.join(os.getcwd(), directory))
		print('Processing {} files in directory {}'.format(len(files), directory))
		for i in range(len(files)):
			in_file = files[i]
			path = os.path.join(os.getcwd(), directory, in_file)
			word_position = compute_word_position(path)
			labeled_position = compute_labeled_position(path, word_position)
			unlabeled_position = compute_unlabeled_position(labeled_position, word_position, max_span=3)
			positive_feature_vector += compute_feature_vector(word_position, labeled_position, normalize_vector)
			negative_feature_vector += compute_feature_vector(word_position, unlabeled_position, normalize_vector)
			message = '{} of {} files done, processing {}'.format(i+1, len(files), in_file)
			print(message, end='\r')
			sys.stdout.flush()
		print()

		# Compute number of examples to write
		positive_length = len(positive_feature_vector) if labeled_num == -1 else min(labeled_num, len(positive_feature_vector))
		negative_length = len(negative_feature_vector) if unlabeled_num == -1 else min(unlabeled_num, len(negative_feature_vector))
		if use_multiplier:
			negative_length = int(positive_length * multiplier)

		# Filter negative examples
		negative_feature_vector = filter_negtive_example(negative_feature_vector, total_len=negative_length, cap_percent=percent_all_capitalized)

		# Generate random index
		positive_range = random.sample(range(len(positive_feature_vector)), positive_length) if filtering_type == 'randomized' else [i for i in range(positive_length)]
		negative_range = random.sample(range(len(negative_feature_vector)), negative_length) if filtering_type == 'randomized' else [i for i in range(negative_length)]
		
		# Write to file
		with codecs.open(filename, 'w+', 'utf-8') as output:
			output.write(','.join(positive_feature_vector[0].keys()) + '\n')
			for i in positive_range:
				value_list = []
				for s in positive_feature_vector[i].keys():
					value = positive_feature_vector[i][s]
					if s in normalize_vector_constant:
						low, high = normalize_vector_constant[s][0], normalize_vector_constant[s][1]
						value = normalize_scale_factor * (value - low) / (high - low)
						pass
					value_list += ['{:.6f}'.format(value)]
				try:
					output.write(','.join(value_list) + '\n')
				except Exception as e:
					pass				
			for i in negative_range:
				value_list = []
				for s in negative_feature_vector[i].keys():
					value = negative_feature_vector[i][s]
					if s in normalize_vector_constant:
						low, high = normalize_vector_constant[s][0], normalize_vector_constant[s][1]
						value = normalize_scale_factor * (value - low) / (high - low)
						pass
					value_list += ['{:.6f}'.format(value)]
				try:
					output.write(','.join(map(str, value_list)) + '\n')
				except Exception as e:
					pass

			# Report
			print('Output filename: {}'.format(filename))
			print('Vector filtering type: {}'.format(filtering_type))
			print('Number of positive vector written: {}'.format(positive_length))
			print('Number of negative vector written: {}'.format(negative_length))
			print('Feature vector width {}'.format(len(positive_feature_vector[0])))
