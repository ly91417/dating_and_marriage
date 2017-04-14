# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-04-11 13:32:30
# @Last Modified by:   charlotte
# @Last Modified time: 2017-04-14 11:44:46

import re
import os
import csv
import pandas as pd

def read_raw_table(file):
	id_dict = {}
	id_regex = re.compile(r'^\d+')
	with open(file, 'r') as f:
		id_dict[-1] = next(f)	# header
		for line in f:
			match = id_regex.search(line)
			id_dict[int(match.group())] = line
	return id_dict

def read_match_table(file):
	match_list_A = []
	match_list_B = []
	with open(file, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		next(reader)	# skip header
		for row in reader:
			match_list_A += [int(row[0])]
			match_list_B += [int(row[1])]
	return match_list_A, match_list_B

def filter_orig_tuples(orig_dict, match_list):
	match_tuples = []
	for list_id in match_list:
		match_tuples += [orig_dict[list_id]]
	return match_tuples

if __name__ == '__main__':
	raw_data_dir = '../raw_data'
	managed_data_dir = '../managed_data'
	orig_A_files = ['tripadvisor_crawling_result.csv']
	orig_B_files = ['yelp_crawling_result.csv']
	match_file = ['matched_table.csv']
	filtered_files = ['Table_A.csv', 'Table_B.csv']
	set_filename = 'set.csv'
	# Read original files
	id_dict_A, id_dict_B = {}, {}
	for file in orig_A_files:
		id_dict_A.update( read_raw_table(os.path.join(raw_data_dir, file)) )
	for file in orig_B_files:
		id_dict_B.update( read_raw_table(os.path.join(raw_data_dir, file)) )

	# Read matching list
	match_list_A, match_list_B = None, None
	for file in match_file:
		match_list_A, match_list_B = read_match_table(os.path.join(managed_data_dir, file))

	# Filter tuples based on matching
	match_tuples_A = filter_orig_tuples(id_dict_A, match_list_A)
	match_tuples_B = filter_orig_tuples(id_dict_B, match_list_B)

	# Write to files
	with open(os.path.join(managed_data_dir, filtered_files[0]), 'w') as f:
		f.write(id_dict_A[-1])
		for row in match_tuples_A:
			f.write(row)
	with open(os.path.join(managed_data_dir, filtered_files[1]), 'w') as f:
		f.write(id_dict_B[-1])
		for row in match_tuples_B:
			f.write(row)
	
	# Concatenate table A and table B into new csv file
	tableA = pd.read_csv(os.path.join(managed_data_dir, filtered_files[0]))
	tableB = pd.read_csv(os.path.join(managed_data_dir, filtered_files[1]))
	Atitles = {title:'A_{}'.format(title) for title in list(tableA)}
	Btitles = {title:'B_{}'.format(title) for title in list(tableB)}
	newA = tableA.rename(columns=Atitles)
	newB = tableB.rename(columns=Btitles)
	table_all = pd.concat([newA, newB],axis=1)
	table_all.to_csv(os.path.join(managed_data_dir, set_filename),index=False)
