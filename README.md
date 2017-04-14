CS838 Project Stage 4 Report
University of Wisconsin-Madison
Fan Wu, Wei Li, Ying Li    {fwu49,wli284,li528}@wisc.edu

How did you combine the two tables A and B to obtain E? 
To decide the schema of E, we looked into the raw data file we crawled from TripAdvisor and Yelp instead of the table we obtained in stage 3 (the table of matching entities, with a few columns removed for sake of matching). The final schema for table E is shown as follows:

(title,phone,tags,price,yelp_rating,food_rating,service_rating,value_rating,atmosphere_rating,feature,street_address,zipcode,zipcode_extension,monday,tuesday,wednesday,thursday,friday,saturday,sunday,webpage)

#Note that the attributes in bold is the features generated from combination of common attributes in Table A table and Table B.

The schema for Table E is the combination of table A and B with the same columns merged and different columns unioned.

Schema for Table A (From TripAdvisor Data):
(id, title, popularity, rating, price, cuisine, phone, food_rating, service_rating, value_rating, atmosphere_rating, price_range, feature, mon, tue, wed, thu, fri, sat, sun, address, description)

Schema for Table B (From Yelp Data:
(id, title, yelpPage, categories, price, rating, mon, tue, wed, thu, fri, sat, sun, addr, reservations, delivery, takeout, creditCard, applePay, bikeParking, goodForKids, goodForGroups, attire, noiseLevel, alcohol, outdoorSeating, wifi, hasTV, waiterService, caters, phone, goodFor, parking, ambience, driveThrough)

A python script is used to do the merging, as we will discuss later.

Did you add any other table? 

We did not add any other table.

Since we cannot obtain Table E directly from Table A and B, we use the id of rows in table A and B to locate the corresponding rows in the original comprehensive tables where A and B are derived. The id field is not shown in the schema above, because it is used merely to facilitate the translation of rows between multiple tables.

When you did the combination, did you run into any issues?

By looking at Table A and B, we found that a few entries have titles in gibberish, which are stemmed from the web crawling process. Our solution is to use the value without any gibberish when possible. If both values contain gibberish, we use a rule to decide which one to keep. We will discuss the rule in details later.

Also, we ran into the issue of missing values. If either the value from A or B is missing, we use the value of the other Table. If both values are missing, there is nothing we can do at this point, and thus we leave the field empty.

Discuss the combination process in detail, e.g., when you merge tuples, what are the merging functions (such as to merge two age values, always select the age value from the tuple from Table A, unless this value is missing in which case we select the value from the tuple in Table B). 

title: we want to use the title without any gibberish. The rule is to firstly remove any gibberish in the value to get the cleaned string, then to choose the longer string for more information purposes. We also run the values through the str.title() function to get a nice string format. The following is an example.
Example:
Table A: george‰Û¡ÌÝåÁÌÎÌÌ´åÈs zoo liquor deli
Table B: cafÌÎÌ_Ì´å© at the opera
Table E: George's Zoo Liquor Deli

price: we combined two data sources and unioned the price range from Table A and Table B by keeping the maximum and minimum prices. There are some cases when Table B only contains strings like “pricy”, “moderate” and table A have null values, we keep those strings.
	Example:
	Table A: NULL
	Table B: inexpensive
	Table E: inexpensive (this will be transformed into 25% of the price distribution when performing the analysis )

Table A: $15 -$30
	Table B: $20 -$40
	Table E: $15 -$40

phone: we first converted all phone numbers to the (xxx) xxx-xxxx format using regular expressions. Some phone numbers have the additional country code, so we removed that. If two phone numbers do not agree we kept them both. And if a phone number has a length less than 10, we simply dropped it and chose the other one.

Example: 
Table A: +1 415-673-0557
Table B: (628) 444-3666
Table E: (415) 673-0557 or (628) 444-3666

tags: this attribute is used to indicate the category of cuisine. In this category field, we unioned two category lists from Table A and Table B to eliminate the redundant features. 
Example: 
Table A: Japanese, Chinese
Table B: Japanese, French, Chinese.
Table E: Japanese, Chinese, French.

street_address: similarly to title, we first examined if the address contains the gibberish characters and removed the gibberish characters from the address string. We keep the longer value for more information purposes. Also we removed the zipcode and zipcode extension using regex, as they will have their own columns.
Example: (street_address)
Table A: 200 Jackson Street,San Francisco, CA 94111-1806
Table B: 200 Jackson StSan Francisco, CA 94111
Table E: 200 Jackson Street

zipcode: Zipcode is extracted from address selected by the rule of street_address line using regular expression.
Example: 
Table A: 200 Jackson Street,San Francisco, CA 94111-1806
Table B: 200 Jackson StSan Francisco, CA 94111
Table E: 94111

zipcode_extension: Zipcode_extension is extracted from the raw address selected by the rule of street_address line using regular expression.
Example: 
Table A: 200 Jackson Street,San Francisco, CA 94111-1806
Table B: 200 Jackson StSan Francisco, CA 94111
Table E: 1806

features:  For this column we combined features from TripAdvisor and Yelp. The two values have different formats. The value from TripAdvisor is given as a list, and the value from Yelp is given as a set of boolean values. For example: takeout=Yes, delivery=No, etc. Our final form contains a list of features. Also, we use the set union to remove any duplicates. The following is an example.
Example:
	Table A: Deliver, Drive-through
	Table B: deliver=Yes, take-out=No, ApplePay=Yes
	Table E: Deliver, Derive-through, ApplePay

trip_food_rating,  trip_service_rating, trip_atmosphere_rating,  trip_ vaule_rating, trip_price_range, yelp_Page,  yelp_rating, yelp_price: We directly copied from table A or table B, since there is no much meaning in combining these attributes. In detail, the tripAdvisor data set contain 5 kind of ratings while yelp only have one overall rating. It is necessary to keep all the data for later analysis. Thus, all these features were decided to be kept without any merging steps.

Hours: the original values contain only one entry for the week. After merging, we have an individual column for each day in the week. We used the regular expression to extract the time in a day. In situation of inconsistent values, we calculated the hours conservatively in the sense that we always choose the later opening time and the earlier closing time. Moreover, a restaurant could have multiple intervals of operation (the owner decides to take an one-hour break in the morning etc.). We also kept the information. The following is an example.

Example 1:
	Table A: 11:30 am - 5:00 pm
Table B: 11:00 am - 4:30 pm
Table E: 11:30 AM - 4:30 PM

Example 2:
	Table A: 11:30 am - 10:00 pm
Table B: 11:30 am-2:30 pm 5:30 pm-10:00 pm
Table E: 11:30 AM-2:30 PM, 5:30 PM-10:00 PM

Statistics on Table E: specifically, what is the schema of Table E, how many tuples are in Table E? Give at least four sample tuples from Table E. 
final schema for table E:
(title,phone,tags,price,yelp_rating,food_rating,service_rating,value_rating,atmosphere_rating,feature,street_address,zipcode,zipcode_extension,monday,tuesday,wednesday,thursday,friday,saturday,sunday,webpage)

and there exist 980 rows of tuples in table E, the  following is the 4 examples for tuples:

Kokkari Estiatorio,(415)981-0983,"Mediterranean,Greek", $25-$80,4.5,4.5/5,4.5/5,4.5/5,4/5,"Serves Alcohol, Applepay, Seating, Waitstaff, Parking, Wheelchair Accessible, Full Bar, Private Dining, Alcohol, Valet Parking, Reservations, Delivery, Attire",200 Jackson Street,94111,1806,"11:30 AM-2:30 PM, 5:30 PM-10:00 PM","11:30 AM-2:30 PM, 5:30 PM-10:00 PM","11:30 AM-2:30 PM, 5:30 PM-10:00 PM","11:30 AM-2:30 PM, 5:30 PM-10:00 PM","11:30 AM-2:30 PM, 5:30 PM-11:00 PM",5:00 PM-11:00 PM,5:00 PM-10:00 PM,http://www.yelp.com/ /biz/kokkari-estiatorio-san-francisco

Taylor Street Coffee Shop,(415) 567-4031,"American, Contemporary, Cafe, Breakfast & Brunch, Burgers, Sandwiches",$11-$30,4.0,4.5/5,4.5/5,4/5,4.5/5,"Applepay, Seating, Waitstaff, Noiselevel, Takeout, Creditcard, Parking, Attire",375 Taylor street,94102,2004,7:00 AM-2:00 PM,7:00 AM-2:00 PM,7:00 AM-2:00 PM,7:00 AM-2:00 PM,7:00 AM-2:00 PM,7:00 AM-2:00 PM,7:00 AM-2:00 PM,https://www.yelp.com/ /biz/taylor-street-coffee-shop-san-francisco

Quince,(415) 775-8500,"French, Italian",$61-$300,4.0,4.5/5,4.5/5,4.5/5,4/5,"Reservations, Serves Alcohol, Applepay, Seating, Waitstaff, Accepts Discover, Parking, Wheelchair Accessible, Accepts Mastercard, Full Bar, Accepts American Express, Private Dining, Valet Parking, Accepts Visa, Parking Available, Delivery, Alcohol",470 Pacific avenue,94133,4610,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:00 PM-9:00 PM,5:00 PM-9:00 PM,,https://www.yelp.com/ /biz/quince-san-francisco

Piqueos,(415) 282-8812,"Peruvian, Latin, Spanish, Latin American",$15-$60,4.0,4.5/5,4.5/5,4/5,4/5,"Serves Alcohol, Applepay, Seating, Waitstaff, Parking, Alcohol, Caters, Creditcard, Reservations, Delivery, Attire",830 Cortland avenue,94110,,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:30 PM-9:00 PM,5:30 PM-10:00 PM,5:30 PM-10:00 PM,5:30 PM-9:00 PM,http://www.yelp.com/ /biz/piqueos-san-francisco


Append the code of the Python script to the end of this pdf file. 

Instruction to run the code:
# Sort Table A, Table B by matching id
cd script
python raw_data_extraction.py
python select_original_entries.py
# perform schema matching
python schema_merging.py
# The filename of the combined table is  Table_E.csv
Source Code:
raw_data_extraction.py
schema_merging.py
select_original_entries.py



Suggestions for the instructor:
We figured out that jupyter notebook don’t work well with auto-merge with the git because formatting reasons. So, we recommend later semesters students to use different filenames to avoid conflict. Otherwise if there is any good ways to improve the conflict in git by using jupyter, please let us know.

