#!/usr/bin/env python 

#Run the maximum entropy classifier on *all* the H1N1 tweets.

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
	conn = MySQLdb.connect(host=DATABASES['default']['HOST'], 
			user=DATABASES['default']['USER'], 
			passwd=DATABASES['default']['PASSWORD'], 
			db=DATABASES['default']['NAME'])

	training_tweets = classify.get_training_tweets(conn_analysis)
	training_feature_set = classify.process_tweets(training_tweets)

	config_megam('/opt/packages')
	classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)

	count_table = {'+':0, '-':0, 'I':0, 'O':0}  
	tweets = classify.get_tweets_to_classify(conn_analysis);

	for tweet in tweets:
		text = classify.get_tweet_text(conn_analysis, tweet[0])[0][0]
		guess = classifier.classify(classify.process_tweet(text))
		update_tweet_polarity(tweet[0], guess, conn_analysis)
		count_table[guess] += 1

	#For the tweets where polarity was determined manually, copy from 
	#majority_vote to auto_vote
	fix_manual_tweets(conn_analysis)

	print count_table

if __name__ == '__main__':
	main_function()
