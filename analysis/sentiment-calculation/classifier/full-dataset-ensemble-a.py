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

def update_max_ent_ensemble(tweet_id, polarity, conn):
	'''Update the classifier rating if the maximum entropy classifier has 
	predicted I, or O'''

	if polarity in ('I', 'O'):
		cursor = conn.cursor()
		sql = classify.Statements.UPDATE_AUTO % (polarity, tweet_id)
		cursor.execute(sql)
		
		conn.commit()
		cursor.close()

def fix_manual_tweets(conn):
	classify.run_sql(conn, classify.Statements.UPDATE_MANUAL_CLASSIFIED)

def main_function():
	conn_analysis = MySQLdb.connect(host="localhost", user="root", passwd="tanzania", db="twitter_heart")

	training_tweets = classify.get_training_tweets(conn_analysis)
	training_feature_set = classify.process_tweets(training_tweets)

	tweets = classify.get_tweets_to_classify(conn_analysis);

	bayes_classifier = NaiveBayesClassifier.train(training_feature_set)
	count_table = {'+':0, '-':0, 'I':0, 'O':0}  

	for tweet in tweets:
		text = classify.get_tweet_text(conn_analysis, tweet[0])[0][0]
		guess = bayes_classifier.classify(classify.process_tweet(text))
		classify.update_tweet_polarity(tweet[0], guess, conn_analysis)
		count_table[guess] += 1

	print "Naive Bayes"
	print count_table

	count_table = {'+':0, '-':0, 'I':0, 'O':0}  
	config_megam('/opt/packages')
	max_ent_classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)

	for tweet in tweets:
		text = classify.get_tweet_text(conn_analysis, tweet[0])[0][0]
		guess = max_ent_classifier.classify(classify.process_tweet(text))
		update_max_ent_polarity(tweet[0], guess, conn_analysis)
		count_table[guess] += 1

	#For the tweets where polarity was determined manually, copy from 
	#majority_vote to auto_vote
	fix_manual_tweets(conn_analysis)

	print "Maximum Entropy"
	print count_table

if __name__ == '__main__':
	main_function()
