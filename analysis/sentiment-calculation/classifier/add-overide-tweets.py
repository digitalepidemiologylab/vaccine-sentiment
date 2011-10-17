#!/usr/bin/env python 
import MySQLdb
import csv
from database_settings import DATABASES

def main_function():
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])

	reader = csv.reader(open('tweet-list.txt'), delimiter=",")

	cursor = conn.cursor()

	for x in reader:
		SQL = "UPDATE sentiment_sentimentconsensus SET test_tweet = true WHERE tweet_id = '%s'" % x[0]
		cursor.execute(SQL)

	conn.commit()
	cursor.close()

if __name__ == '__main__':
	main_function()
