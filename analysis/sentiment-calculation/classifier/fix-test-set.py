#!/usr/bin/env python 

import MySQLdb
import numpy 
import pylab
from database_settings import DATABASES

class Statements:	
	MIN_TEST_VOTES = '44'

	TWEETS_VOTES_SQL = "SELECT tweet_id, COUNT(*) AS vote_count FROM sentiment_sentiment  "
	TWEETS_VOTES_SQL += "GROUP BY tweet_id HAVING vote_count > " + MIN_TEST_VOTES

def get_tweets_with_enough_votes(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.TWEETS_VOTES_SQL)

	rows = list(cursor.fetchall())
	tweet_ids = [x[0] for x in rows]
	
	cursor.close()
	return tweet_ids

def is_test_tweet(tweet_id, conn):
	SENTIMENT_SQL = "SELECT tweet_id, vote, COUNT(*) AS vote_count FROM sentiment_sentiment "
	SENTIMENT_SQL += "WHERE tweet_id='%s' " % tweet_id
	SENTIMENT_SQL += " GROUP BY VOTE "

	cursor = conn.cursor()
	cursor.execute(SENTIMENT_SQL);

	rows = list(cursor.fetchall())
	majority_vote = max(rows, key=lambda x: x[2])
	remaining_count = sum([x[2] for x in rows if x[1] != majority_vote])

	if majority_vote[2] > (1 + remaining_count/2):
		#ok to be test tweet
		return True
	else:
		#discard this tweet from the test set
		return False
	cursor.close()

def write_consensus_to_database(data, conn):
	cursor = conn.cursor()
	for x in data:
		(tweet_id, is_test_tweet) = x
		SQL = None;

		if is_test_tweet:
			SQL = "UPDATE sentiment_sentimentconsensus SET test_tweet = true WHERE tweet_id = '%s'" % tweet_id
			print tweet_id
		else:
			SQL = "UPDATE sentiment_sentimentconsensus SET test_tweet = false WHERE tweet_id = '%s'" % tweet_id
		cursor.execute(SQL)

	conn.commit()
	cursor.close()

def process_tweets(tweet_ids, conn):
	consensus_data = []
	for tweet_id in tweet_ids:
		test_tweet = is_test_tweet(tweet_id, conn)	
		consensus_data.append((tweet_id, test_tweet))

	write_consensus_to_database(consensus_data, conn)
	return consensus_data
	
def main_function():
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])
	tweet_counts = get_tweets_with_enough_votes(conn)
	process_tweets(tweet_counts, conn)
	conn.commit()
	conn.close()

if __name__ == '__main__':
	main_function()
