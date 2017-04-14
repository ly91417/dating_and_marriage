# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-03-28 14:27:38
# @Last Modified by:   charlotte
# @Last Modified time: 2017-04-14 11:59:38

import re
import csv
import os
import pandas as pd
from functools import reduce

# Read all lines into an list, grouped by chunks
def read_chunks(input_file):
	content = []
	with open(input_file) as f:
		chunk = []
		delim = '----------------------------------------------------------------'
		start = False
		for line in f:
			line = line.strip('\n\t ')
			# print('line: {}'.format(line))
			if start:
				if not line:
					start = False
					content += [chunk]
					chunk = []
					# print('end of a chunk')
				else:
					chunk += [line]
			elif line == delim:
				start = True
				# print('start of a chunk')
			else:
				continue
	return content

# Parse and clean each chunk into a map
def process_chunk(chunk, _id, schema):
	result = {}
	regex = re.compile(r'^(\w+:)')
	for line in chunk:
		match = regex.match(line)
		tag = match.group()[:-1].strip()
		value = line[match.end():].strip()
		result[tag] = value
		if tag not in schema:
			schema += [tag]		# keep trach of schema

	result['id'] = _id
	return result


if __name__ == '__main__':

	raw_data_dir = '../raw_data'
	raw_files_A = ['tripadvisor_crawling_result.txt']
	raw_files_B = ['yelp_crawling_price_1.txt', 'yelp_crawling_price_2.txt', 'yelp_crawling_price_3.txt', 'yelp_crawling_price_4.txt']

	# Process table A
	_id = 0
	for file in raw_files_A:
		num_processed = 0
		chunks = read_chunks(os.path.join(raw_data_dir, file))
		schema = ['id']
		with open(os.path.join(raw_data_dir, file[:-4] + '.csv'), 'w') as csvfile:
			chunk_dicts = []
			for chunk in chunks:
				chunk_dicts += [process_chunk(chunk, _id, schema)]
				_id += 1
			writer = csv.DictWriter(csvfile, fieldnames=schema)
			writer.writeheader()
			for d in chunk_dicts:
				writer.writerow(d)
				num_processed += 1
		print('number of entries from {}: {}'.format(file, num_processed))

	# Process table B
	_id = 0
	for file in raw_files_B:
		num_processed = 0
		chunks = read_chunks(os.path.join(raw_data_dir, file))
		schema = ['id']
		with open(os.path.join(raw_data_dir, file[:-4] + '.csv'), 'w') as csvfile:
			chunk_dicts = []
			for chunk in chunks:
				chunk_dicts += [process_chunk(chunk, _id, schema)]
				_id += 1
			writer = csv.DictWriter(csvfile, fieldnames=schema)
			writer.writeheader()
			for d in chunk_dicts:
				writer.writerow(d)
				num_processed += 1
		print('number of entries from {}: {}'.format(file, num_processed))

	# Write B as a sngle file
	temp_table = []
	for filename in raw_files_B:
		file = os.path.join(raw_data_dir, filename[:-4] + '.csv')
		temp_table += [pd.read_csv(file)]

	header = []
	for df in temp_table:
		for title in df.columns.tolist():
			if title not in header:
				header += [title]

	# [df.columns.tolist() for df in temp_table]
	# header = list(set(reduce(lambda x,y: x+y, header)))
	table_B = pd.concat(temp_table)
	table_B = table_B[header]
	table_B.to_csv(os.path.join(raw_data_dir, 'yelp_crawling_result.csv'), index=False)



