# -*- coding: utf-8 -*-
# @Author: Charlotte
# @Date:   2017-02-27 16:16:26
# @Last Modified by:   charlotte
# @Last Modified time: 2017-02-28 18:32:07

# cd ../data/; python2 article_select.py -p=0.5; cd ../ml_package/

from shutil import copyfile
from shutil import rmtree
import os
import random
import argparse

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description=' ')
	parser.add_argument('-p', '--percent', type=float, help=' ')
	parser.add_argument('-d', '--directory', type=str, help=' ')
	args = parser.parse_args()
	percent = args.percent if args.percent else 0.5
	dir_name = args.directory if args.directory else 'labeled'

	file_list = list(os.listdir(os.path.join(os.getcwd(), dir_name)))
	dev_set_len = int(len(file_list) * (1 - percent))
	test_set_len = len(file_list) - dev_set_len
	dev_set_index = random.sample(range(len(file_list)), dev_set_len)
	test_set_index = list(set(range(len(file_list))) - set(dev_set_index))

	# Create output directory
	directory = 'devl_set'
	if os.path.exists(directory):
		rmtree(directory)
	os.makedirs(directory)
	for f in dev_set_index:
		filename = file_list[f]
		source = os.path.join(os.getcwd(), dir_name, filename)
		dest = os.path.join(os.getcwd(), directory, filename)
		copyfile(source, dest)

	# Create output directory
	directory = 'test_set'
	if os.path.exists(directory):
		rmtree(directory)
	os.makedirs(directory)
	for f in test_set_index:
		filename = file_list[f]
		source = os.path.join(os.getcwd(), dir_name, filename)
		dest = os.path.join(os.getcwd(), directory, filename)
		copyfile(source, dest)
