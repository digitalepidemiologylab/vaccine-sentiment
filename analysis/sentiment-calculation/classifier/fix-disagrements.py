#!/usr/bin/env python 

#We fix manually rated tweets that have been rated differently by the classifier

#Salathe: Now, re the question of whether the classifier should take precedence over the
#student rating. Here I think we should do the following. First, we don't touch
#the test set because we are sure about these tweets. For all other tweets,
#assign the rating of the classifier to every tweet, treating it the classifier
#as a student. Then, for all tweets, take the rating of the student with the
#highest accuracy; that's our rating.

import MySQLdb
from database_settings import DATABASES

class Statements:
	SQL_RATINGS = "SELECT vote, accuracy from sentiment_sentiment ss, rater_accuracy ra " 
	SQL_RATINGS += "WHERE ss.user_id = ra.user_id and tweet_id = %s" 

	SQL_TWEETS = "SELECT tweet_id, majority_vote, auto_vote FROM sentiment_sentimentconsensus " 
	SQL_TWEETS += "WHERE auto_vote <> majority_vote AND test_tweet = false"

	CLASSIFIER_ACCURACY = "SELECT accuracy from rater_accuracy where user_id = 100";


def get_qualifying_tweets(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.SQL_TWEETS)

	rows = list(cursor.fetchall())
	cursor.close()

	return rows

def fix_contention(tweet, classifier_accuracy, conn):
	tweet_id, majority_vote, auto_vote = tweet

	cursor = conn.cursor()
	cursor.execute(Statements.SQL_RATINGS % tweet_id)

	rows = list(cursor.fetchall())
	rows.append((auto_vote, classifier_accuracy))

	#sort on accuracy
	rows.sort(key=lambda x: x[1])

	#get the rating that corresponds to the highest accuracy
	new_rating = rows[-1][0]

	#update the database with the new rating
	SQL = "UPDATE sentiment_sentimentconsensus SET auto_vote = '%s' WHERE tweet_id = %s"  % (new_rating, tweet_id)
	cursor.execute(SQL)

	print rows
	print new_rating

	conn.commit()
	cursor.close()

def get_classifier_accuracy(conn):
	''' Retrive the accuracy of the classifier '''
	cursor = conn.cursor()
	cursor.execute(Statements.CLASSIFIER_ACCURACY)
	accuracy = cursor.fetchall()[0][0]
	cursor.close()

	return accuracy

def main_function():
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])

	tweets = get_qualifying_tweets(conn)

	classifier_accuracy = get_classifier_accuracy(conn)

	for tweet in tweets:
		fix_contention(tweet, classifier_accuracy, conn)

if __name__ == '__main__':
	main_function()
