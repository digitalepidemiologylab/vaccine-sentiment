#!/usr/bin/env python 

# I initially loaded the data set with out the tweet date. Here we go through the original data file, 
# and add in the dates. 

import csv
import MySQLdb
from database_settings import DATABASES

def tweet_date(filename):
	f = csv.reader(open(filename), delimiter=';', quotechar='"')
	data = []

	for x in f:
		tweet_id = x[0]
		tweet_date = x[3]

		data.append((tweet_id, tweet_date))
	return data	

def add_dates(data):
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
				user=DATABASES['default']['USER'], 
				passwd=DATABASES['default']['PASSWORD'], 
				db=DATABASES['default']['NAME'])

	cursor = conn.cursor()

	for d in data:
		(tweet_id, tweet_date) = d

		SQL = "UPDATE tweets_tweet SET timestamp = '%s'" % tweet_date
		SQL += " WHERE tweet_id=%s" % tweet_id

		print SQL
		cursor.execute(SQL)

	conn.commit()
	cursor.close()

if __name__ == '__main__':
	data = tweet_date('no_check_in/full-data-no-friends-followers-text-fixed.csv')
	add_dates(data)
