################################################################
##	Filename: 	crawler_tripadvisor.py				
##	Author: 	Charlotte
##	Email: 		cbgitek@gmail.com
##	Create:   	2017-02-07
##	Modified: 	2017-02-08
################################################################

from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import urllib2
import time
import random
import re
import argparse
import sys
import os

html_file = './html_pages/nytimes.html'

# Generate URL and issue crawling calls
def crawl(out_file):
	result = crawl_page(html_file)
	post_processing(result)
	write_result(result, out_file)
	return

# Extract information from the page
def crawl_page(file_path):
	extract_results = []
	# Read from HTML file
	html_data = open(file_path, 'r').read()
	# Remove <!-- ... --> parts
	html_data = re.sub(re.compile("<!--.*?-->",re.DOTALL),"", html_data)
	# Wrap by soup
	soup = BeautifulSoup(html_data)

	# Retrive all paragraphs
	try:
		paragraphs = soup.findAll('div', attrs={'class':'g-blurb-text'})
		# print(paragraphs)
	except Exception as e:
		print('Error retrieving list of paragraphs: {}'.format(str(e)))
	# Save each paragraph
	for p in paragraphs:
		# print(p.__dict__)
		try:
			# After debugging I realized the content is in the second <p> tag
			new_entry = p.findAll('p')[0].getText()
			# print(new_entry.encode('utf-8'))
			extract_results += [new_entry]
		except Exception as e:
			print('Error retrieving individual paragraph: {}'.format(str(e)))
	return extract_results

# Remove unwanted tokens
def post_processing(raw_data):
	for i in range(len(raw_data)):
		processed = raw_data[i]
		processed = re.sub(re.compile(' &amp',re.DOTALL), '', processed)
		raw_data[i] = processed


# Write result to a file
def write_result(result, out_file):
	# Create output directory
	directory = 'nytimes_articles'
	if not os.path.exists(directory):
	    os.makedirs(directory)

	suffix = 0
	for r in result:
		with open('./{0}/{1}_{2}.txt'.format(directory, out_file, suffix), 'w+') as f:
			f.write(r.encode('utf-8'))
		suffix += 1

if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(description='Extracts paragraphs for place name classification')
	parser.add_argument('-f', '--filename', type=str, help='Enter the output file name')
	parser.add_argument('-d', '--debug', type=str, help='Enter the debug output file name')
	args = parser.parse_args()
	filename = args.filename if args.filename else 'nytimes'
	# debug = args.debug if args.debug else 'nytimes_crawling_debug_output.txt'
	debug = args.debug if args.debug else '/dev/null'

	# Redirect error output
	# sys.stdout = open(debug, 'w+')
	# sys.stderr = open(debug, 'w+')

	# Start the crawler
	crawl(filename)
