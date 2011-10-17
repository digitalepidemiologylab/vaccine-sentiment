#!/usr/bin/env python 

import MySQLdb
import classify

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk import config_megam
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import TrigramAssocMeasures
from nltk.classify import accuracy 
from nltk.stem import PorterStemmer
from database_settings import DATABASES

def process_bigrams(conn, polarity):
	cursor = conn.cursor()
	cursor.execute(Statements.GRAM_SQL % polarity)

	rows = list(cursor.fetchall())
	print rows[0]
	cursor.close()

def get_training_tweets(conn):
	return classify.run_sql(conn, classify.Statements.TRAINING_TWEETS)

def get_test_tweets(conn):
	return classify.run_sql(conn, classify.Statements.TEST_TWEETS)

def update_tweet_polarity(tweet_id, polarity, conn):
	cursor = conn.cursor()

	sql = classify.Statements.CHECK_CONSENSUS % tweet_id
	cursor.execute(sql)
	result = cursor.fetchall()
	print result

	if len(result) > 0:
		sql = classify.Statements.UPDATE_AUTO % (polarity, tweet_id)
		print sql
	else:
		sql = classify.Statements.INSERT_AUTO % (tweet_id, polarity)
		print sql

	conn.commit()
	cursor.close()

	update_cursor = conn.cursor()
	update_cursor.execute(sql)

	conn.commit()
	update_cursor.close()

def fix_manual_tweets(conn):
	classify.run_sql(conn, classify.Statements.UPDATE_MANUAL_CLASSIFIED)

def main_function():
	conn = MySQLdb.connect(host=DATABASES['date_cutoff']['HOST'], 
			user=DATABASES['date_cutoff']['USER'], 
			passwd=DATABASES['date_cutoff']['PASSWORD'], 
			db=DATABASES['date_cutoff']['NAME'])

	training_tweets = get_training_tweets(conn)
	training_feature_set = classify.process_tweets(training_tweets)

	classifier = NaiveBayesClassifier.train(training_feature_set)

	error_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	count_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	guess_dict = {'+':0, '-':0, 'I':0, 'O':0} 

	full_matrix = {'+':{'+':0, '-':0, 'I':0, 'O':0}, 
				'-':{'+':0, '-':0, 'I':0, 'O':0}, 
				'I':{'+':0, '-':0, 'I':0, 'O':0}, 
				'O':{'+':0, '-':0, 'I':0, 'O':0}}

	count_table = {'+':0, '-':0, 'I':0, 'O':0}  

	test_tweets = get_test_tweets(conn)
	test_feature_set = classify.process_tweets(test_tweets)

	classifier_accuracy = accuracy(classifier, test_feature_set)

	print count_table
	print "classifier accuracy: " + repr(classifier_accuracy)

	#for tweet in tweets:
	#	text = classify.get_tweet_text(conn, tweet[0])[0][0]
	#	guess = classifier.classify(classify.process_tweet(text))
	#	update_tweet_polarity(tweet[0], guess, conn)
	#	count_table[guess] += 1

	#For the tweets where polarity was determined manually, copy from 
	#majority_vote to auto_vote
	#fix_manual_tweets(conn)

	#test_tweets = get_test_tweets(conn)
	#test_feature_set = process_tweets(test_tweets)


	#for f in test_tweets:
	#	guess = classifier.classify(process_tweet(f[1]))
	#	full_matrix[f[2]][guess] += 1
	#	update_tweet_polarity(f[0], guess, conn)
	#	if (guess == '-') or (guess == '+'):
	#print full_matrix


if __name__ == '__main__':
	main_function()
