#!/usr/bin/env python 

import MySQLdb
import classify
from nltk.classify import NaiveBayesClassifier
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import TrigramAssocMeasures
from nltk.classify import accuracy 
from database_settings import DATABASES

full_matrix = {'+':{'+':0, '-':0, 'I':0, 'O':0}, 
				'-':{'+':0, '-':0, 'I':0, 'O':0}, 
				'I':{'+':0, '-':0, 'I':0, 'O':0}, 
				'O':{'+':0, '-':0, 'I':0, 'O':0}}

def update_tweet_polarity_ensemble(tweet_id, polarity, conn):
	cursor = conn.cursor()

	sql = classify.Statements.CHECK_CONSENSUS % tweet_id
	cursor.execute(sql)

	result = cursor.fetchall()

	entropy_polarity = result[0][0]

	conn.commit()
	cursor.close()

	update_cursor = conn.cursor()

	if entropy_polarity != polarity:
		full_matrix[entropy_polarity][polarity] += 1
		sql = classify.Statements.UPDATE_NOT_CLASSIFIED % (tweet_id)
		update_cursor.execute(sql)

	conn.commit()
	update_cursor.close()

def main_function():
	conn = MySQLdb.connect(host=DATABASES['ensemble']['HOST'], 
			user=DATABASES['ensemble']['USER'], 
			passwd=DATABASES['ensemble']['PASSWORD'], 
			db=DATABASES['ensemble']['NAME'])

	training_tweets = classify.get_training_tweets(conn)
	training_feature_set = classify.process_tweets(training_tweets)
	classifier = NaiveBayesClassifier.train(training_feature_set)

	error_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	count_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	guess_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	
	count_table = {'+':0, '-':0, 'I':0, 'O':0}  
	tweets = classify.get_tweets_to_classify(conn);

	for tweet in tweets:
		text = classify.get_tweet_text(conn, tweet[0])[0][0]
		guess = classifier.classify(classify.process_tweet(text))
		classify.update_tweet_polarity(tweet[0], guess, conn)
		count_table[guess] += 1

	#fix_manual_tweets(conn_analysis)
	classify.run_sql(conn, classify.Statements.UPDATE_MANUAL_CLASSIFIED)

	print count_table
	print full_matrix

if __name__ == '__main__':
	main_function()
