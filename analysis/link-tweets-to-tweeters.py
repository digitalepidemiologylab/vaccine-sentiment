#!/usr/bin/env python 

# Take the original dataset, and link tweets to tweeters. 

import csv
import MySQLdb
from database_settings import DATABASES

def tweet_tweeter(filename):
	f = csv.reader(open(filename), delimiter=';', quotechar='"')
	data = []

	for x in f:
		tweet_id = x[0]
		tweeter_name = x[1]
		tweeter_user_id = x[-1]

		data.append((tweet_id, tweeter_name, tweeter_user_id))
	return data

def get_tweeter_id(user_name, twitter_user_id, conn):
	cursor = conn.cursor()

	SQL = "SELECT id FROM tweeter_tweeter WHERE user_name='%s' " % user_name

	if twitter_user_id !='0':
		SQL += "AND twitter_user_id=%s " % twitter_user_id

	cursor.execute(SQL)
	rows = cursor.fetchall()

	tweeter_id = rows[0][0]

	cursor.close()
	return tweeter_id

def link_tweets_to_tweeters(data):
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
				user=DATABASES['default']['USER'], 
				passwd=DATABASES['default']['PASSWORD'], 
				db=DATABASES['default']['NAME'])
	cursor = conn.cursor()

	for d in data:
		(tweet_id, tweeter_name, twitter_user_id) = d
		tweeter_id = get_tweeter_id(tweeter_name, twitter_user_id, conn)

		LINK_SQL = "UPDATE tweets_tweet SET tweeter_id = %s " % tweeter_id
		LINK_SQL += " WHERE tweet_id=%s" % tweet_id

		cursor.execute(LINK_SQL)

	conn.commit()
	cursor.close()

if __name__ == '__main__':
	data = tweet_tweeter('no_check_in/full-data-no-friends-followers-text-fixed.csv')
	link_tweets_to_tweeters(data)
