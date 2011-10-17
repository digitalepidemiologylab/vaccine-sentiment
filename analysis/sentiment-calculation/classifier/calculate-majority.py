#!/usr/bin/env python 

#Compute the majority rating for each manually rated tweet

import MySQLdb
import numpy 
import pylab
from database_settings import DATABASES

class Statements:	
	TWEETS_VOTES_SQL = "SELECT tweet_id, COUNT(*) AS vote_count FROM sentiment_sentiment  "
	TWEETS_VOTES_SQL += "GROUP BY tweet_id"

def get_tweets_with_enough_votes(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.TWEETS_VOTES_SQL)

	rows = list(cursor.fetchall())
	tweet_ids = [x[0] for x in rows]
	
	cursor.close()
	return tweet_ids

def get_votes_for_tweet(tweet_id, conn):
	SENTIMENT_SQL = "SELECT tweet_id, vote, COUNT(*) AS vote_count FROM sentiment_sentiment "
	SENTIMENT_SQL += "WHERE tweet_id='%s' " % tweet_id
	SENTIMENT_SQL += " GROUP BY VOTE "

	cursor = conn.cursor()
	cursor.execute(SENTIMENT_SQL);

	rows = list(cursor.fetchall())

	majority_vote = max(rows, key=lambda x: x[2])
	vote_count = reduce(lambda x,y: x + y[2], rows, 0)
	percentage_consensus = float(majority_vote[2])/vote_count

	cursor.close()
	return (majority_vote[1], percentage_consensus, vote_count)

def generate_quality_of_votes_histogram(percentages):
	(n, bins) = numpy.histogram(percentages)

	pylab.xlabel('Percentage Majority')
	pylab.ylabel('Number of tweets')
	pylab.text(1.0, 1.0, 'SK')
	pylab.plot(.5*(bins[1:]+bins[:-1]), n)
	pylab.savefig('quality-of-votes.png')

def write_consensus_to_database(data, conn):
	cursor = conn.cursor()
	for x in data:
		(tweet_id, vote, percentage, vote_count) = x

		INSERT_SQL = "INSERT INTO sentiment_sentimentconsensus (tweet_id, majority_vote, majority_percentage, num_votes) "
		INSERT_SQL += "VALUES (%s, '%s', %s, %s)" % (tweet_id, vote, percentage, vote_count)

		print INSERT_SQL
		cursor.execute(INSERT_SQL)

	conn.commit()
	cursor.close()

def process_tweets(tweet_ids, conn):
	percentages = []
	consensus_data = []
	for tweet_id in tweet_ids:
		r = get_votes_for_tweet(tweet_id, conn)	
		vote, percentage, vote_count = r
		percentages.append(percentage)
		consensus_data.append((tweet_id, vote, percentage, vote_count))

	write_consensus_to_database(consensus_data, conn)
	generate_quality_of_votes_histogram(percentages)
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
