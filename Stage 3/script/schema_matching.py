# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-03-28 14:27:38
# @Last Modified by:   charlotte
# @Last Modified time: 2017-04-02 23:02:56

import re
import csv

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
def process_chunk_tripadvisor(chunk, _id):
	result = {}
	filter_list = ['price', 'price_range', 'popularity', 'food_rating', 'service_rating', 'value_rating', 'atmosphere_rating', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'description']
	regex = re.compile(r'^(\w+:)')
	for line in chunk:
		match = regex.match(line)
		tag = match.group()[:-1]
		if tag in filter_list:
			continue
		value = line[match.end():]
		# Transforming and cleaning values
		if tag == 'title':
			value = value[1:]
			result[tag] = value
		elif tag == 'address':
			address = value.strip()
			# Zipcode 5 digit
			zipcode_re = re.compile(r'CA \d{5}')
			match = zipcode_re.search(address)
			if match:
				result['zipcode'] = match.group()[3:]
			# Zipcode extension
			# zipcode_ext_re = re.compile(r'-\d{4}')
			# match = zipcode_ext_re.search(address)
			# if match:
			# 	result['zipcode_ext'] = match.group()[1:]
			# Street address
			city_re = re.compile(r'[,]*San Francisco')
			match = city_re.search(address)
			if match:
				street = address[:match.start()]
				result['street_addr'] = replace_abbr_in_address(street)
		elif tag == 'rating':
			pass
			# 	result[tag] = value[:-13]
		elif tag == 'price':
			pass
		elif tag == 'price_range':
			pass
		elif tag == 'cuisine':
			result[tag] = value
		elif tag == 'phone':
			value = re.sub(r'[\s\+\-\(\)]', '', value)			
			if len(value) == 11:
				value = value[1:]
			value = '' + value[0:3] + value[3:]
			result[tag] = value
		else:
			result[tag] = value
		result['id'] = _id
	return result

# Parse each chunk into a map
def process_chunk_yelp(chunk, _id):
	result = {}
	filter_list = ['price', 'price_range', 'yelpPage', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
	feature_list = ['takeout', 'creditCard', 'applePay', 'parking', 'bikeParking', 'outdoorSeating', 'wifi', 'caters', 'attire', 'ambience', 'waiterService', 'hasTV', 'reservations', 'goodForKids', 'noiseLevel', 'goodFor', 'delivery', 'goodForGroups', 'alcohol', 'driveThrough']
	features = []
	regex = re.compile(r'^(\w+:)')
	for line in chunk:
		match = regex.match(line)
		tag = match.group()[:-1]
		if tag in filter_list:
			continue
		value = line[match.end():]
		# Transforming and cleaning values
		if tag == 'title':
			value = value[1:]
			result[tag] = value
		elif tag in feature_list:
			avail = line[match.end()+1:]
			if avail == 'Yes':
				features += [tag]
		elif tag == 'addr':
			address = value.strip()
			# Zipcode 5 digit
			zipcode_re = re.compile(r'CA \d{5}')
			match = zipcode_re.search(address)
			if match:
				result['zipcode'] = match.group()[3:]
			# Zipcode extension
			# zipcode_ext_re = re.compile(r'-\d{4}')
			# match = zipcode_ext_re.search(address)
			# if match:
			# 	result['zipcode_ext'] = match.group()[1:]
			# Street address
			city_re = re.compile(r'[,]*San Francisco')
			match = city_re.search(address)
			if match:
				street = address[:match.start()]
				result['street_addr'] = replace_abbr_in_address(street)
		elif tag == 'rating':
			pass
			# 	result[tag] = value[:-12]
		elif tag == 'categories':
			result['cuisine'] = value
		elif tag == 'phone':
			value = re.sub(r'[\s\+\-\(\)]', '', value)			
			if len(value) == 11:
				value = value[1:]
			value = '' + value[0:3] + value[3:]
			result[tag] = value
		else:
			result[tag] = value
		result['id'] = _id
		result['feature'] = ', '.join(features)
	return result

def replace_abbr_in_address(address):
	result = address
	result = re.sub(r'(\sbldg\s)|(\sbldg$)|(\sbldg[\.\,])', ' building ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\save\s)|(\save$)|(\save[\.\,])', ' avenue ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\sst\s)|(\sst$)|(\sst[\.\,])', ' street ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\sblvd\s)|(\sblvd$)|(\sblvd[\.\,])', ' boulevard ', result, flags=re.IGNORECASE)
	if result and result[-1] == ' ':
		result = result[:-1]
	return result

if __name__ == '__main__':

	fieldnames = ['id', 'title', 'cuisine', 'phone', 'feature', 'zipcode', 'street_addr']
	num_processed = 0
	_id = 0
	filename = 'tripadvisor_crawling_result'
	input_file = '../raw_data/' + filename + '.txt'
	content = read_chunks(input_file)
	with open('../managed_data/' + filename + '.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for chunk in content:
			chunk_map = process_chunk_tripadvisor(chunk, _id)
			_id += 1
			writer.writerow(chunk_map)
			num_processed += 1
	print('number of entries from {}: {}'.format(filename, num_processed))

	num_processed = 0
	_id = 0
	filenames = ['yelp_crawling_price_1', 'yelp_crawling_price_2', 'yelp_crawling_price_3', 'yelp_crawling_price_4', 'yelp_crawling_price_5']
	for filename in filenames:
		input_file = '../raw_data/' + filename + '.txt'
		content = read_chunks(input_file)
		with open('../managed_data/' + filename + '.csv', 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for chunk in content:
				chunk_map = process_chunk_yelp(chunk, _id)
				_id += 1
				writer.writerow(chunk_map)
				num_processed += 1
	print('number of entries from {}: {}'.format('yelp_crawling_price', num_processed))










