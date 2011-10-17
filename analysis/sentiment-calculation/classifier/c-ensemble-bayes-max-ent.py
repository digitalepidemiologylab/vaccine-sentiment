#!/usr/bin/env python 

#This runs ensemble strategies, combining the naive bayes and maximum entropy classifiers. 

import MySQLdb
import classify

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk import config_megam
from nltk.classify import accuracy 
from database_settings import DATABASES

def update_tweet_polarity_ensemble(tweet_id, polarity, conn):
	cursor = conn.cursor()

	sql = classify.Statements.CHECK_CONSENSUS % tweet_id
	cursor.execute(sql)

	result = cursor.fetchall()

	prev_polarity = result[0][0]

	conn.commit()
	cursor.close()

	update_cursor = conn.cursor()

	if prev_polarity != polarity:
		sql = classify.Statements.UPDATE_NOT_CLASSIFIED % (tweet_id)
		update_cursor.execute(sql)

	conn.commit()
	update_cursor.close()

def fix_manual_tweets(conn):
	classify.run_sql(conn, classify.Statements.UPDATE_MANUAL_CLASSIFIED)

def main_function():
	conn = MySQLdb.connect(host=DATABASES['ensemble']['HOST'], 
			user=DATABASES['ensemble']['USER'], 
			passwd=DATABASES['ensemble']['PASSWORD'], 
			db=DATABASES['ensemble']['NAME'])

	training_tweets = classify.get_training_tweets(conn)
	training_feature_set = classify.process_tweets(training_tweets)

	bayes_classifier = NaiveBayesClassifier.train(training_feature_set)

	count_table = {'+':0, '-':0, 'I':0, 'O':0}  

	test_tweets = classify.get_test_tweets(conn)

	for tweet in test_tweets:
		text = classify.get_tweet_text(conn, tweet[0])[0][0]
		guess = bayes_classifier.classify(classify.process_tweet(text))
		classify.update_tweet_polarity(tweet[0], guess, conn)
		count_table[guess] += 1

	print "Naive Bayes"
	print count_table

	count_table = {'+':0, '-':0, 'I':0, 'O':0}  
	config_megam('/opt/packages')
	max_ent_classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)

	for tweet in test_tweets:
		text = classify.get_tweet_text(conn, tweet[0])[0][0]
		guess = max_ent_classifier.classify(classify.process_tweet(text))
		update_tweet_polarity_ensemble(tweet[0], guess, conn)
		count_table[guess] += 1

	print "Maximum Entropy"
	print count_table

	for tweet in test_tweets:
		text = classify.get_tweet_text(conn, tweet[0])[0][0]
		result = classify.run_sql(conn, classify.Statements.CHECK_CONSENSUS % tweet[0])
		guess = result[0][0]

		if guess is None:
			bayes_guess = bayes_classifier.classify(classify.process_tweet(text))
			entropy_guess = max_ent_classifier.classify(classify.process_tweet(text))

			if bayes_guess in ('+', '-'):
				classify.update_tweet_polarity(tweet[0], bayes_guess, conn)
			if entropy_guess in ('I', 'O') and bayes_guess not in ('+', '-'):
				classify.update_tweet_polarity(tweet[0], entropy_guess, conn)
			
	#generate the accuracy matrix
	full_matrix = {'+':{'+':0, '-':0, 'I':0, 'O':0}, 
				'-':{'+':0, '-':0, 'I':0, 'O':0}, 
				'I':{'+':0, '-':0, 'I':0, 'O':0}, 
				'O':{'+':0, '-':0, 'I':0, 'O':0}}

	for tweet in test_tweets:
		result = classify.run_sql(conn, classify.Statements.CHECK_CONSENSUS % tweet[0])
		guess = result[0][0]

		actual_result = classify.run_sql(conn, classify.Statements.CHECK_MAJORITY % tweet[0])
		actual = actual_result[0][0]

		if guess is not None:
			if actual is not None:
				full_matrix[actual][guess] += 1

	print full_matrix

if __name__ == '__main__':
	main_function()
