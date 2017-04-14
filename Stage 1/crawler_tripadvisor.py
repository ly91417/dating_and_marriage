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

root_url = 'https://www.tripadvisor.com'

# Disable javascript on browser for this to work
get_url = lambda offset: \
				'{}/Restaurants-g60713-oa{}-San_Francisco_California.html#EATERY_LIST_CONTENTS'.format(root_url, offset)

# Generate URL and issue crawling calls
def crawl(start_offset=0, stride=30, end_offset=30, filename='tripAdvisor_results.txt'):
	# By default, a page has 30 entries
	for offset in range(start_offset, end_offset, stride):
		page_url = get_url(offset)
		result = crawl_page(page_url)
		write_result(result, filename)
		time.sleep(random.randint(1, 2))

# Extract information from a page listing a number of resturants
def crawl_page(page_url):
	extract_results = []
	try:
		# Read from URL
		soup = BeautifulSoup(urllib2.urlopen(page_url).read())
		# Retrieve the top level list
		restaurant_list = soup.findAll('div', attrs={'class':re.compile(r'^listing listingIndex')})
		# Read information from individual list entry
		for r in restaurant_list:
			new_entry = {}
			# Extract title
			try:
				new_entry['title'] = r.find('a', attrs={'class':'property_title'}).getText()
			except Exception, e:
				print('Error retrieving title: {}'.format(str(e)))
			# Extract popularity
			try:
				new_entry['popularity'] = r.find('div', attrs={'class':'popIndex popIndexDefault'}).getText()
			except Exception, e:
				print('Error retrieving popularity: {}'.format(str(e)))
			# Extract rating
			try:
				new_entry['rating'] = r.find('img', attrs={'class':'sprite-ratings'})['alt']
			except Exception, e:
				print('Error retrieving rating: {}'.format(str(e)))
			# Extract price range
			try:
				new_entry['price'] = r.find('span', attrs={'class':'price_range'}).getText()
			except Exception, e:
				print('Error retrieving price range: {}'.format(str(e)))
			# Click into individual pages
			try:
				entry_url = r.find('a', attrs={'class':'property_title'})['href']
				crawl_individual_page(new_entry, urljoin(root_url, entry_url))
			except Exception, e:
				print('Error walking into individual page: {}'.format(str(e)))			
			# Add the new entry to result
			extract_results += [new_entry]
	except Exception, e:
		print('Error retrieving webpage: {}'.format(str(e)))

	return extract_results

# Extract information from a page dedicated to a single restaurant
def crawl_individual_page(new_entry, page_url):
	try:
		# Read from URL
		soup = BeautifulSoup(urllib2.urlopen(page_url).read())
		# Extract cuisine
		try:
			new_entry['cuisine'] = soup.find('div', attrs={'class':'detail separator'}).getText()
		except Exception, e:
			print('Error retrieving cuisine: {}'.format(str(e)))
		# Extract phone number
		try:
			new_entry['phone'] = soup.find('div', attrs={'class':'fl phoneNumber'}).getText()
		except Exception, e:
			print('Error retrieving phone number: {}'.format(str(e)))
		# Read detail tab
		try:
			details = soup.find('div', attrs={'class':'content_block details_block scroll_tabs'})
			# Extract detailed ratings
			try:
				ratings = details.findAll('div', attrs={'class':'ratingRow wrap'})
				for r in ratings:
					# Food rating
					try:
						if r.find('span', attrs={'class':'text'}).getText() == 'Food':
							new_entry['food_rating'] = r.find('img', attrs={'class':re.compile(r'^sprite-rating_s_fill')})['alt']
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
					# Service rating
					try:
						if r.find('span', attrs={'class':'text'}).getText() == 'Service':
							new_entry['service_rating'] = r.find('img', attrs={'class':re.compile(r'^sprite-rating_s_fill')})['alt']
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
					# Value rating
					try:
						if r.find('span', attrs={'class':'text'}).getText() == 'Value':
							new_entry['value_rating'] = r.find('img', attrs={'class':re.compile(r'^sprite-rating_s_fill')})['alt']
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
					# Atomosphere rating
					try:
						if r.find('span', attrs={'class':'text'}).getText() == 'Atmosphere':
							new_entry['atmosphere_rating'] = r.find('img', attrs={'class':re.compile(r'^sprite-rating_s_fill')})['alt']
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
				rows = details.findAll('div', attrs={'class':'row'})
				for r in rows:
					# Extract price range
					try:
						if r.find('div', attrs={'class':'title'}).getText() == 'Average prices':
							new_entry['price_range'] = r.find('div', attrs={'class':'content'}).getText().replace('\n', '')
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
					# Extract restaurant features
					try:
						if r.find('div', attrs={'class':'title'}).getText() == 'Restaurant features':
							new_entry['feature'] = r.find('div', attrs={'class':'content'}).getText().replace('\n', '')
					except Exception, e:
						print('Error retrieving detailed ratings: {}'.format(str(e)))
				# Extract hours
				try:
					hours_content = details.find('div', attrs={'class':'hours content'}).findAll('div', attrs={'class':'detail'})
					for h in hours_content:
						try:
							day = h.find('span', attrs={'class':'day'}).getText()
							hour = h.find('div', attrs={'class':'hoursRange'}).getText()
							if day == 'Monday':
								new_entry['mon'] = hour
							elif day == 'Tuesday':
								new_entry['tue'] = hour
							elif day == 'Wednesday':
								new_entry['wed'] = hour
							elif day == 'Thursday':
								new_entry['thu'] = hour
							elif day == 'Friday':
								new_entry['fri'] = hour
							elif day == 'Saturday':
								new_entry['sat'] = hour
							elif day == 'Sunday':
								new_entry['sun'] = hour
						except Exception, e:
							print('Error retrieving hours: {}'.format(str(e)))
				except Exception, e:
						print('Error retrieving hours: {}'.format(str(e)))
				# Extract address
				try:
					address = details.find('span', attrs={'class':'format_address'}).getText()
					# locality = details.find('span', attrs={'class':'locality'}).getText()
					new_entry['address'] = ', '.join([address])
				except Exception, e:
					print('Error retrieving address: {}'.format(str(e)))
				# Extract description
				try:
					description = details.find('div', attrs={'class':'additional_info'}).find('div', attrs={'class':'content'}).getText().replace('\n', '')
					new_entry['description'] = description
				except Exception, e:
					print('Error retrieving description: {}'.format(str(e)))

			except Exception, e:
				print('Error retrieving detailed ratings: {}'.format(str(e)))

		except Exception, e:
			print('Error retrieving detail tab: {}'.format(str(e)))

	except Exception, e:
		print('Error retrieving webpage: {}'.format(str(e)))


# Write result to a file
def write_result(result, filename):
	with open(filename, 'a') as f:
		for r in result:
			# Replace newline with space
			# Encode in UTF8
			f.write('----------------------------------------------------------------\n')
			f.write('title: {}\n'.format(r.get('title', '').replace('\n', ' ').encode('utf-8')))
			f.write('popularity: {}\n'.format(r.get('popularity', '').replace('\n', ' ').encode('utf-8')))
			f.write('rating: {}\n'.format(r.get('rating', '').replace('\n', ' ').encode('utf-8')))
			f.write('price: {}\n'.format(r.get('price', '').replace('\n', ' ').encode('utf-8')))
			f.write('cuisine: {}\n'.format(r.get('cuisine', '').replace('\n', ' ').encode('utf-8')))
			f.write('phone: {}\n'.format(r.get('phone', '').replace('\n', ' ').encode('utf-8')))
			f.write('food_rating: {}\n'.format(r.get('food_rating', '').replace('\n', ' ').encode('utf-8')))
			f.write('service_rating: {}\n'.format(r.get('service_rating', '').replace('\n', ' ').encode('utf-8')))
			f.write('value_rating: {}\n'.format(r.get('value_rating', '').replace('\n', ' ').encode('utf-8')))
			f.write('atmosphere_rating: {}\n'.format(r.get('atmosphere_rating', '').replace('\n', ' ').encode('utf-8')))
			f.write('price_range: {}\n'.format(r.get('price_range', '').replace('\n', ' ').encode('utf-8')))
			f.write('feature: {}\n'.format(r.get('feature', '').replace('\n', ' ').encode('utf-8')))
			f.write('mon: {}\n'.format(r.get('mon', '').replace('\n', ' ').encode('utf-8')))
			f.write('tue: {}\n'.format(r.get('tue', '').replace('\n', ' ').encode('utf-8')))
			f.write('wed: {}\n'.format(r.get('wed', '').replace('\n', ' ').encode('utf-8')))
			f.write('thu: {}\n'.format(r.get('thu', '').replace('\n', ' ').encode('utf-8')))
			f.write('fri: {}\n'.format(r.get('fri', '').replace('\n', ' ').encode('utf-8')))
			f.write('sat: {}\n'.format(r.get('sat', '').replace('\n', ' ').encode('utf-8')))
			f.write('sun: {}\n'.format(r.get('sun', '').replace('\n', ' ').encode('utf-8')))
			f.write('address: {}\n'.format(r.get('address', '').replace('\n', ' ').encode('utf-8')))
			f.write('description: {}\n'.format(r.get('description', '').replace('\n', ' ').encode('utf-8')))
			f.write('\n')

if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(description='Extracts restaurant information from tripadvisor.com')
	parser.add_argument('-s', '--start', type=int, help='Enter the start offset (needs to be a multiply of 30')
	parser.add_argument('-e', '--end', type=int, help='Enter the end offset (needs to be a multiply of 30')
	parser.add_argument('-f', '--filename', type=str, help='The file the results will be saved to')
	parser.add_argument('-d', '--debug', type=str, help='The file to output debug information')
	args = parser.parse_args()
	start_offset = args.start if args.start else 0
	end_offset = args.end if args.end else 30
	filename = args.filename if args.filename else 'tripadvisor_crawling_result.txt'
	debug = args.debug if args.debug else 'tripadvisor_crawling_debug_output.txt'
	# Redirect error output
	sys.stdout = open(debug, 'w+')
	# Start the crawler
	crawl(start_offset, 30, end_offset, filename)
