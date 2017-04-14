__author__ = 'Lucas Ou-Yang, Mathew Sprehn'
__date__ = 'July 4th, 2013'
"""
We can be suboptimal, eg: like parse w/ beautifulsoup and not use mthreading
because Yelp will rate limit us anyways. This entire project was just for
fun, there are better scraping solutions out there and scraping yelp is
looked down upon anyways, read their robots.txt.

Check out my main scraping project, newspaper, for news extraction!
https://github.com/codelucas/newspaper
"""
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import urllib2
import argparse
import re
import codecs
import time
import random
import ssl

get_yelp_page = \
	lambda zipcode, page_num, price_range: \
		'https://www.yelp.com/search?find_loc={0}&start={1}&attrs=RestaurantsPriceRange2.{2}'.format(zipcode, page_num, price_range)

context = ssl._create_unverified_context()
        
ZIP_URL = "zipcodes.txt"
FIELD_DELIM = u'###'
LISTING_DELIM = u'((('

def get_zips():
	"""
	"""
	f = open(ZIP_URL, 'r+')
	zips = [int(zz.strip()) for zz in f.read().split('\n') if zz.strip() ]
	f.close()
	return zips

def crawl_page(zipcode, page_num, price_range, verbose=False):
	"""
	This method takes a page number, yelp GET param, and crawls exactly
	one page. We expect 10 listing per page.
	"""
	try:
		page_url = get_yelp_page(zipcode, page_num, price_range)
		soup = BeautifulSoup(urllib2.urlopen(page_url, context=context).read())
		print('Starting crawling from: {}'.format(page_url))

	except Exception, e:
		print str(e)
		return []

	# print('page_url: {}'.format(page_url))

	# Locate every li entry, 10 entries are in a page
	restaurants = soup.findAll('div', attrs={'class':re.compile
			(r'^search-result natural-search-result')})
	try:
		assert(len(restaurants) == 10)
	except AssertionError, e:
		# We make a dangerous assumption that yelp has 10 listing per page,
		# however this can also be a formatting issue, so watch out
		print 'we have hit the end of the zip code', str(e)
		# False is a special flag, returned when quitting
		return [], False

	extracted = [] # a list of tuples
	for r in restaurants:

		yelpPage = ''
		title = ''
		rating = ''
		addr = ''
		phone = ''
		categories = ''
		price = ''
		mon = ''
		tue = ''
		wed = ''
		thu = ''
		fri = ''
		sat = ''
		sun = ''
		healthInspection = ''
		reservations = ''
		delivery = ''
		takeout = ''
		creditCard = ''
		applePay = ''
		goodFor = ''
		parking = ''
		bikeParking = ''
		goodForKids = ''
		goodForGroups = ''
		attire = ''
		ambience = ''
		noiseLevel = ''
		alcohol = ''
		outdoorSeating = ''
		wifi = ''
		hasTV = ''
		waiterService = ''
		driveThrough = ''
		caters = ''

		# Extract title
		try:
			title = r.find('a', {'class':'biz-name js-analytics-click'}).getText()
		except Exception, e:
			if verbose: print 'title extract fail', str(e)

		# Extract Yelp page link
		try:
			yelpPage = r.find('a', {'class':'biz-name js-analytics-click'})['href']
		except Exception, e:
			if verbose: print 'yelp page link extraction fail', str(e)
			continue

		# Extract category
		try:
			categories = r.findAll('span', {'class':'category-str-list'})
			categories = ', '.join([c.getText() for c in categories if c.getText()])
		except Exception, e:
			if verbose: print "category extract fail", str(e)

		# Extract rating
		try:
			rating = r.find('div', {'class':re.compile(r'^i-stars')})['title']
		except Exception, e:
			if verbose: print "rating extract fail", str(e)

		# Extract address
		try:
			addr = r.find('div', {'class':'secondary-attributes'}).address.getText()
		except Exception, e:
			if verbose: print 'address extract fail', str(e)
		
		# Extract phone number
		try:
			phone = r.find('span', {'class':'biz-phone'}).getText()
		except Exception, e:
			if verbose: print 'phone extract fail', str(e)

		time.sleep(random.randrange(1, 10))

		# Walk into pages for individual restaurants
		try:
			soup2 = BeautifulSoup(urllib2.urlopen(urljoin('https://www.yelp.com', yelpPage), context=context).read())

			# Extract price range
			try:
				price = soup2.find('dd', {'class':'nowrap price-description'}).getText()
			except Exception, e:
				if verbose: print 'price extract fail', str(e)

			# Extract hours
			try:
				hourTable = soup2.find('table', {'class':'table table-simple hours-table'}).findAll('tr')
				for day in hourTable:
					whichDay = day.th.getText()
					hoursLine = day.td.getText()
					if whichDay == 'Mon':
						mon = hoursLine
					elif whichDay == 'Tue':
						tue = hoursLine
					elif whichDay == 'Wed':
						wed = hoursLine
					elif whichDay == 'Thu':
						thu = hoursLine
					elif whichDay == 'Fri':
						fri = hoursLine
					elif whichDay == 'Sat':
						sat = hoursLine
					elif whichDay == 'Sun':
						sun = hoursLine
			except Exception, e:
				if verbose: print "hours extract fail", str(e)

			# Extract information from detail table
			try:
				dl_data = soup2.findAll('dl')
				for dlitem in dl_data:
					if dlitem.dt.getText() == 'Takes Reservations':
						reservations = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Delivery':
						delivery = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Take-out':
						takeout = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Accepts Credit Cards':
						creditCard = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Accepts Apple Pay':
						applePay = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Good For':
						goodFor = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Parking':
						parking = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Bike Parking':
						bikeParking = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Good for Kids':
						goodForKids = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Good for Groups':
						goodForGroups = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Attire':
						attire = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Ambience':
						ambience = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Noise Level':
						noiseLevel = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Alcohol':
						alcohol = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Outdoor Seating':
						outdoorSeating = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Wi-Fi':
						wifi = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Has TV':
						hasTV = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Waiter Service':
						waiterService = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Drive-Thru':
						driveThrough = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'Caters':
						caters = dlitem.dd.getText()
					elif dlitem.dt.getText() == 'nowrap health-score-description':
						healthInspection = dlitem.dd.getText()

			except Exception, e:
				if verbose: print 'detail information extract fail', str(e)
			
		except Exception, e:
			if verbose: print "**failed to get you a page", str(e)

		print '----------------------------------------------------------------'
		if title: print 'title:', title.encode('utf-8')
		if yelpPage: print 'yelpPage:', 'http://www.yelp.com/', yelpPage.encode('utf-8')
		if categories: print 'categories:', categories.encode('utf-8')
		if price: print 'price:', price.encode('utf-8')
		if rating: print 'rating:', rating.encode('utf-8')
		if mon: print 'mon:', mon.encode('utf-8')
		if tue: print 'tue:', tue.encode('utf-8')
		if wed: print 'wed:', wed.encode('utf-8')
		if thu: print 'thu:', thu.encode('utf-8')
		if fri: print 'fri:', fri.encode('utf-8')
		if sat: print 'sat:', sat.encode('utf-8')
		if sun: print 'sun:', sun.encode('utf-8')
		if addr: print 'addr:', addr.encode('utf-8')
		if phone: print 'phone:', phone.encode('utf-8')
		if reservations: print 'reservations:', reservations.encode('utf-8')
		if delivery: print 'delivery:', delivery.encode('utf-8')
		if takeout: print 'takeout:', takeout.encode('utf-8')
		if creditCard: print 'creditCard:', creditCard.encode('utf-8')
		if applePay: print 'applePay:', applePay.encode('utf-8')
		if goodFor: print 'goodFor:', goodFor.encode('utf-8')
		if parking: print 'parking:', parking.encode('utf-8')
		if bikeParking: print 'bikeParking:', bikeParking.encode('utf-8')
		if goodForKids: print 'goodForKids:', goodForKids.encode('utf-8')
		if goodForGroups: print 'goodForGroups:', goodForGroups.encode('utf-8')
		if attire: print 'attire:', attire.encode('utf-8')
		if ambience: print 'ambience:', ambience.encode('utf-8')
		if noiseLevel: print 'noiseLevel:', noiseLevel.encode('utf-8')
		if alcohol: print 'alcohol:', alcohol.encode('utf-8')
		if outdoorSeating: print 'outdoorSeating:', outdoorSeating.encode('utf-8')
		if wifi: print 'wifi:', wifi.encode('utf-8')
		if hasTV: print 'hasTV:', hasTV.encode('utf-8')
		if waiterService: print 'waiterService:', waiterService.encode('utf-8')
		if driveThrough: print 'driveThrough:', driveThrough.encode('utf-8')
		if caters: print 'caters:', caters.encode('utf-8')
		print('\n')

		# extracted.append((title, categories, rating, img, addr, phone, price, menu,
		#    creditCards, parking, attire, groups, kids, reservations, delivery, takeout,
		#    waiterService, outdoor, wifi, goodFor, alcohol, noise, ambience, tv, caters,
		#    wheelchairAccessible))

	return extracted, True

def crawl(price_range, zipcode=None):
	
	page = 0
	flag = True
	if zipcode is None:
		print('Attempting to extract near San Francisco with price range {}'.format(price_range))
		zipcode = r'San+Francisco,+CA'
	else:
		print('Attempting to extract near zipcode <{}> with price range {}'.format(zipcode, price_range))

	# Ten entries per page, automatically go to next page by adding 10
	while flag:
		extracted, flag = crawl_page(zipcode, page, price_range)
		if not flag:
			print('Extraction Done')
			break
		page += 10
		time.sleep(random.randrange(1, 10))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Extracts all yelp restaurant \
		data from a specified zip code (or all American zip codes if nothing \
		is provided)')
	parser.add_argument('-z', '--zipcode', type=int, help='Enter a zip code \
		you\'t like to extract from.')
	parser.add_argument('-p', '--price', type=int, help='A number between 1 and 4')

	args = parser.parse_args()
	crawl(args.price, args.zipcode)
