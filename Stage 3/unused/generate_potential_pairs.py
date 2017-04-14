# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-03-27 15:32:55
# @Last Modified by:   charlotte
# @Last Modified time: 2017-03-27 16:32:57

import argparse
import itertools  
import xml.etree.ElementTree as ET

def read_xml(filename):
	return ET.parse(filename).getroot()

# Generate exhaustive pairs
def pair_iterator(root_A, root_B):
	list_A = root_A.findall('entity')
	list_B = root_B.findall('entity')
	# print(list_A[0].find('title').text)
	return itertools.product(list_A, list_B)

# Generate a list of pairs that could potentially match
def generate_pairs(all_pairs):
	filtered_pairs = []
	for p in all_pairs:
		# Zipcode
		# print(p[0])
		zipcode_A = p[0].find('address').find('zipcode').text
		zipcode_B = p[1].find('address').find('zipcode').text	
		if zipcode_A != zipcode_B:
			print('zipcode does not match')
			continue

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate a list of pairs that should be further checked for matching')
	parser.add_argument('-ia', '--input_A', type=str, help='XML file [A] after schema matching')
	parser.add_argument('-ib', '--input_B', type=str, help='XML file [B] after schema matching')
	parser.add_argument('-o', '--output', type=str, help='Output XML file containing pairs')
	args = parser.parse_args()
	input_file_a = args.input_A if args.input_A != None else "../managed_data/after_schema_matching.xml"
	input_file_b = args.input_B if args.input_B != None else "../managed_data/after_schema_matching.xml"
	output_file = args.output if args.output != None else "../managed_data/after_blocking.xml"

	root_A = read_xml(input_file_a)
	root_B = read_xml(input_file_b)
	all_pairs = pair_iterator(root_A, root_B)
	filtered_pairs = generate_pairs(all_pairs)

	# for entity in root.findall('entity'):
	# 	title = entity.find('title')
	# 	print(title.text)


