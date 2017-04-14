# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-04-11 15:20:05
# @Last Modified by:   charlotte
# @Last Modified time: 2017-04-14 09:53:25

import os
import csv
import re
import operator

table_A_schema = 'id,title,popularity,rating,price,cuisine,phone,food_rating,service_rating,value_rating,atmosphere_rating,price_range,feature,mon,tue,wed,thu,fri,sat,sun,address,description'.split(',')
table_B_schema = 'id,title,yelpPage,categories,price,rating,mon,tue,wed,thu,fri,sat,sun,addr,reservations,delivery,takeout,creditCard,applePay,bikeParking,goodForKids,goodForGroups,attire,noiseLevel,alcohol,outdoorSeating,wifi,hasTV,waiterService,caters,phone,goodFor,parking,ambience,driveThrough'.split(',')

valid_chars = re.compile(r'[a-zA-Z0-9\'\,\.\:\- ]')
hours_regex = re.compile(r'([0-9]{1,2}\:[0-9]{1,2})[\s]*(am|pm|AM|PM)')
zipcode_re = re.compile(r'CA \d{5}')
zipcode_ext_re = re.compile(r'-\d{4}')
street_re = re.compile(r'[,]*San Francisco')
phone_re = re.compile(r'[0-9]+')

day_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
feature_list = 'reservations,delivery,takeout,creditCard,applePay,bikeParking,goodForKids,goodForGroups,attire,noiseLevel,alcohol,outdoorSeating,wifi,hasTV,waiterService,caters,phone,parking,ambience,driveThrough'.split(',')


def read_tuples(table):
	tuples = []
	with open(table, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		header = list(next(reader))	# read header
		for row in reader:
			tuples += [row]
	return header, tuples


def remove_gibberish(string):
	result = []
	for c in string:
		if valid_chars.match(c):
			result += [c]
	removed_num = 200 if len(string) == 0 else len(string)-len(result)
	return ''.join(result), removed_num


def longer(value_A, value_B):
	return value_A if len(value_A) > len(value_B) else value_B


def merge_title(tuple_A, tuple_B):
	pos_A = table_A_schema.index('title')
	pos_B = table_B_schema.index('title')
	value_A, value_B = tuple_A[pos_A], tuple_B[pos_B]
	clean_A, removed_A = remove_gibberish(value_A)
	clean_B, removed_B = remove_gibberish(value_B)
	if not removed_A and not removed_B:
		return longer(value_A, value_B)
	elif not removed_A:
		return value_A
	elif not removed_B:
		return value_B
	else:
		return longer(clean_A, clean_B).strip().title()


def clean_rating(rating):
	nums = [s for s in rating.split() if s.replace('.','',1).isdigit()]
	new_rating = '/'.join(nums)
	return new_rating


def merge_ratings(tuple_A, tuple_B):
	yelp_rating = clean_rating(tuple_B[table_B_schema.index('rating')])
	trip_food_rating = clean_rating(tuple_A[table_A_schema.index('food_rating')])
	trip_service_rating = clean_rating(tuple_A[table_A_schema.index('service_rating')])
	trip_atmosphere_rating = clean_rating(tuple_A[table_A_schema.index('atmosphere_rating')])
	trip_value_rating = clean_rating(tuple_A[table_A_schema.index('value_rating')])
	return yelp_rating, trip_food_rating, trip_service_rating, trip_atmosphere_rating, trip_value_rating


def merge_webpage(tuple_A, tuple_B):
	yelp_Page = tuple_B[table_B_schema.index('yelpPage')]
	return re.sub(r'\/ \/', '/', yelp_Page)	# fix error in raw data


def merge_price(tuple_A, tuple_B):
	trip_price = tuple_A[table_A_schema.index('price_range')]
	yelp_price = tuple_B[table_B_schema.index('price')]
	prices_A = re.split('\$|-| -|\n', trip_price)
	prices_B = re.split('\$|-| -|\n', yelp_price)
	prices = prices_A + prices_B
	nums = [int(s) for s in prices if s.replace('.', '', 1).isdigit()]
	if len(nums) == 0:
		if len(trip_price)!=0:
			return trip_price
		elif len(yelp_price) != 0:
			return yelp_price
		else:
			return None
	price_range = '${}-${}'.format(min(nums),max(nums))
	return price_range

def merge_addr(tupleA, tuple_B):
	pos_A = table_A_schema.index('address')
	pos_B = table_B_schema.index('addr')
	value_A, value_B = tuple_A[pos_A], tuple_B[pos_B]
	clean_A, removed_A = remove_gibberish(value_A)
	clean_B, removed_B = remove_gibberish(value_B)
	if not removed_A and not removed_B:
		return longer(value_A, value_B)
	elif not removed_A:
		return value_A
	elif not removed_B:
		return value_B
	else:
		return longer(clean_A, clean_B).strip().title()


def merge_category(tuple_A, tuple_B):
	pos_A = table_A_schema.index('cuisine')
	pos_B = table_B_schema.index('categories')
	value_A, value_B = tuple_A[pos_A], tuple_B[pos_B]
	A = value_A.title().split(',')
	B = value_B.title().split(',')
	resulting_list = list(A)
	resulting_list.extend(x for x in B if x not in resulting_list)
	resulting_list = map(lambda x: x.strip().replace(',', ''), resulting_list)
	resulting_list = [x for x in resulting_list if x]
	return ', '.join(resulting_list)


def merge_feature(tuple_A, tuple_B):
	feature = []
	# Get feature from A table
	pos_A = table_A_schema.index('feature')
	value_A = tuple_A[pos_A]
	clean_A, removed_A = remove_gibberish(value_A)
	feature += clean_A.split(', ')
	# Get feature from B table
	for fe in feature_list:
		pos_B = table_B_schema.index(fe)
		if pos_B >= len(tuple_B):
			continue
		value_B = tuple_B[pos_B]
		# clean_B, removed_B = remove_gibberish(value_B)
		if value_B == 'Yes':
			feature += [fe]
	feature = map(lambda x: x.title(), feature)
	feature = list(set(feature))
	return ', '.join([x for x in feature if x])


def merge_phone(tuple_A, tuple_B):
	pos_A = table_A_schema.index('phone')
	pos_B = table_B_schema.index('phone')
	value_A, value_B = tuple_A[pos_A], tuple_B[pos_B]
	clean_A, removed_A = remove_gibberish(value_A)
	clean_B, removed_B = remove_gibberish(value_B)
	match_A = phone_re.findall(clean_A)
	phone_A = None
	if match_A:
		phone_A = ''.join(match_A)
		if len(phone_A) > 10:
			phone_A = phone_A[-10:]
	match_B = phone_re.findall(clean_B)
	phone_B = None
	if match_B:
		phone_B = ''.join(match_B)
		if len(phone_B) > 10:
			phone_B = phone_B[-10:]
	if phone_A == phone_B:
		return format_phone(phone_A)		# nice
	if not phone_A or len(phone_A) is not 10:
		return format_phone(phone_B)
	elif not phone_B or len(phone_B) is not 10:
		return format_phone(phone_A)
	else:
		return '{} or {}'.format(format_phone(phone_A), format_phone(phone_B))


def format_phone(phone):
	if not phone or len(phone) < 10:
		return ''
	else:
		return '({}) {}-{}'.format(phone[:3], phone[3:6], phone[6:])


def merge_hours(tuple_A, tuple_B):
	hours = {}
	for day in day_list:
		hours[day] = merge_hours_on_day(tuple_A, tuple_B, day)
	return hours


def merge_description(tuple_A, tuple_B):
	# only tuple_A has description
	pos_A = table_A_schema.index('description')
	value_A = tuple_A[pos_A]
	clean_A, removed_A = remove_gibberish(value_A)
	return clean_A


def merge_hours_on_day(tuple_A, tuple_B, day):
	pos_A = table_A_schema.index(day)
	pos_B = table_B_schema.index(day)
	value_A, value_B = tuple_A[pos_A], tuple_B[pos_B]
	clean_A, removed_A = remove_gibberish(value_A)
	clean_B, removed_B = remove_gibberish(value_B)
	match_A = hours_regex.findall(clean_A)
	match_B = hours_regex.findall(clean_B)
	hours = None
	if match_A and match_B:
		hours = normalize_hours(match_A, match_B)
	elif match_A:
		hours = match_A
	elif match_B:
		hours = match_B
	# print(hours)
	result = []
	if hours:
		for i in range(0, len(hours), 2):
			line = []
			line.append('{} {}'.format(hours[i][0], hours[i][1].upper()))
			line.append('{} {}'.format(hours[i+1][0], hours[i+1][1].upper()))
			line = ['-'.join(line)]
			result += line
	return ', '.join(result)


def normalize_hours(hour_A, hour_B):
	# both hours have length two (one in the morning and one in the afternoon)
	# choose the hourse conservatively
	morning, afternoon = None, None
	if len(hour_A) == len(hour_B):
		morning_A, morning_B = hour_A[0], hour_B[0]
		morning =  morning_A if compare_hours(morning_A, morning_B) else morning_B
		afternoon_A, afternoon_B = hour_A[-1], hour_B[-1]
		afternoon =  afternoon_A if not compare_hours(afternoon_A, afternoon_B) else afternoon_B
	elif len(hour_A) > 2:
		return hour_A
	elif len(hour_B) > 2:
		return hour_B
	return [morning, afternoon]


def compare_hours(hour_A, hour_B):
	if hour_A[1].lower() == 'pm' and hour_B[1].lower() == 'am':
		return True
	elif hour_A[1].lower() == 'am' and hour_B[1].lower() == 'pm':
		return False
	else:
		split_A = hour_A[0].split(':')
		split_B = hour_B[0].split(':')
		if split_A[0] > split_B[0]:
			return True
		elif split_A[0] < split_B[0]:
			return False
		elif split_A[1] > split_B[1]:
			return True
		else:
			return False


def replace_abbr_in_address(address):
	result = address
	result = re.sub(r'(\sbldg\s)|(\sbldg$)|(\sbldg[\.\,])', ' building ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\save\s)|(\save$)|(\save[\.\,])', ' avenue ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\sst\s)|(\sst$)|(\sst[\.\,])', ' street ', result, flags=re.IGNORECASE)
	result = re.sub(r'(\sblvd\s)|(\sblvd$)|(\sblvd[\.\,])', ' boulevard ', result, flags=re.IGNORECASE)
	if result and result[-1] == ' ':
		result = result[:-1]
	return result


def process_address(address):
	address = replace_abbr_in_address(address).strip()

	zipcode, zipcode_ext, street_addr = None, None, None
	# Zipcode 5 digit
	match = zipcode_re.search(address)
	if match:
		zipcode = match.group()[3:]
	# Zipcode extension
	match = zipcode_ext_re.search(address)
	if match:
		zipcode_ext = match.group()[1:]
	# Street address
	match = street_re.search(address)
	if match:
		street = address[:match.start()]
		street_addr = replace_abbr_in_address(street)

	return zipcode, zipcode_ext, street_addr


if __name__ == '__main__':
	managed_data_dir = '../managed_data'
	table_A_file = 'Table_A.csv'
	table_B_file = 'Table_B.csv'
	table_E_file = 'Table_E.csv'

	header_A, tuples_A = read_tuples(os.path.join(managed_data_dir, table_A_file))
	header_B, tuples_B = read_tuples(os.path.join(managed_data_dir, table_B_file))

	table_E_schema = ['title', 'phone', 'tags', 'price', 'yelp_rating', 'food_rating', 'service_rating', 'value_rating', 'atmosphere_rating', 'feature', 'street_address', 'zipcode', 'zipcode_extension', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'webpage']

	with open(os.path.join(managed_data_dir, table_E_file), 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(table_E_schema)						# header
		for tuple_A, tuple_B in zip(tuples_A, tuples_B):
			line = []
			line += [merge_title(tuple_A, tuple_B)]			# title
			phone = merge_phone(tuple_A, tuple_B)			# phone
			line += [phone]
			line += [merge_category(tuple_A, tuple_B)]		# category
			line += [merge_price(tuple_A,tuple_B)]          # price
			ratings = list(merge_ratings(tuple_A, tuple_B))	# rating
			for rating in ratings:
				line += [rating]
			line += [merge_feature(tuple_A, tuple_B)]		# feature
			address = merge_addr(tuple_A, tuple_B)			# address
			zipcode, zipcode_ext, street_addr = process_address(address)
			line += [street_addr, zipcode, zipcode_ext]
			hours = merge_hours(tuple_A, tuple_B)			# hours
			for day in day_list:
				line += [hours[day]]
			line += [merge_webpage(tuple_A, tuple_B)]		# webpage
			writer.writerow(line)


