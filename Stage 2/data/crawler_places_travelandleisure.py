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

root_url = 'http://www.travelandleisure.com/trip-ideas/best-places-to-travel-in-2017#angra-dos-reis-brazil'

# Generate URL and issue crawling calls
def crawl(filename):
	page_url = root_url
	result = crawl_page(page_url)
	write_result(result, filename)
	return

# Extract information from the page
def crawl_page(page_url):
	extract_results = []
	# Read from URL
	html = urllib2.urlopen(page_url).read()
	# Remove <!-- ... --> parts
	html = re.sub(re.compile("<!--.*?-->",re.DOTALL),"", html)
	# Wrap by soup
	soup = BeautifulSoup(html)

	# Retrive all paragraphs
	try:
		# paragraphs = soup.findAll('p', attrs={'class':'slide-meta__caption', 'data-bind':'html: caption'})
		paragraphs = soup.findAll('div', attrs={'class':'slide-meta'})
		# print(paragraphs)
	except Exception as e:
		print('Error retrieving list of paragraphs: {}'.format(str(e)))
	# Save each paragraph
	for p in paragraphs:
		# print(p.__dict__)
		try:
			# After debugging I realized the content is in the second <p> tag
			new_entry = p.findAll('p')[1].getText()
			# print(new_entry.encode('utf-8'))
			extract_results += [new_entry]
		except Exception as e:
			print('Error retrieving individual paragraph: {}'.format(str(e)))
	return extract_results

# Write result to a file
def write_result(result, filename):
	# Create output directory
	directory = 'lw_articles'
	if not os.path.exists(directory):
	    os.makedirs(directory)

	suffix = 0
	for r in result:
		with open('./{0}/{1}_{2}.txt'.format(directory, filename, suffix), 'w+') as f:
			f.write(r.encode('utf-8'))
		suffix += 1

if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(description='Extracts paragraphs from travelandleisure.com for place name classification')
	parser.add_argument('-f', '--filename', type=str, help='Enter the output file name')
	parser.add_argument('-d', '--debug', type=str, help='Enter the debug output file name')
	args = parser.parse_args()
	filename = args.filename if args.filename else 'travelandleisure'
	# debug = args.debug if args.debug else 'travelandleisure_crawling_debug_output.txt'
	debug = args.debug if args.debug else '/dev/null'

	# Redirect error output
	sys.stdout = open(debug, 'w+')
	sys.stderr = open(debug, 'w+')

	# Start the crawler
	crawl(filename)
