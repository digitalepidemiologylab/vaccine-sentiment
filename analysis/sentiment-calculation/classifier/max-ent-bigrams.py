#!/usr/bin/env python 

#Run the maxmimum entropy classifier use bigrams in the tweets.  

import MySQLdb

from nltk.corpus import stopwords
from nltk import config_megam
from nltk import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import TrigramAssocMeasures
from nltk.classify import accuracy 
from nltk.stem import PorterStemmer
from database_settings import DATABASES

import classify

class Statements:
	NO_MIN_SQL = "SELECT sc.tweet_id, tt.text, sc.majority_vote FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	NO_MIN_SQL += "WHERE sc.tweet_id=tt.id AND sc.num_votes > 2"

	MAJORITY_SQL_ALL = "SELECT sc.tweet_id, tt.text, sc.majority_vote FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	MAJORITY_SQL_ALL += "WHERE majority_percentage > 0.5 "
	MAJORITY_SQL_ALL += "AND sc.tweet_id=tt.id AND sc.num_votes > 2"

	MAJORITY_SQL_PN = "SELECT sc.tweet_id, tt.text, sc.majority_vote FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	MAJORITY_SQL_PN += "WHERE majority_percentage > 0.5 "
	MAJORITY_SQL_PN += "AND sc.tweet_id=tt.id AND sc.num_votes > 2 AND sc.majority_vote IN ('+','-')"

	SINGLE_VOTE_SQL_ALL = "SELECT sc.tweet_id, tt.text, sc.majority_vote FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	SINGLE_VOTE_SQL_ALL += "WHERE sc.num_votes < 3 AND sc.tweet_id=tt.id"

	SINGLE_VOTE_SQL_PN = "SELECT sc.tweet_id, tt.text, sc.majority_vote FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	SINGLE_VOTE_SQL_PN += "WHERE sc.num_votes < 3 AND sc.tweet_id=tt.id AND sc.majority_vote IN ('+', '-')"

	GRAM_SQL = "SELECT tt.text from tweets_tweet tt, sentiment_sentimentconsensus sc WHERE sc.tweet_id = tt.id "
	GRAM_SQL += "AND sc.num_votes < 3 AND majority_vote = '%s'" 

	UPDATE_AUTO = "UPDATE sentiment_sentimentconsensus SET auto_classified=1, "
	UPDATE_AUTO += "auto_vote='%s' WHERE tweet_id=%s"


def fix_tweet_text(text):
	stemmer = PorterStemmer()
	#list_of_words = text.split()
	list_of_words = []

	#bigram_finder = BigramCollocationFinder.from_words(list_of_words)
	bigram_finder = BigramCollocationFinder.from_words(text.split())
	bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 20)

	for bt in bigrams:
		x = "%s %s" % bt
		list_of_words.append(x)

	#trigram_finder = TrigramCollocationFinder.from_words(list_of_words)
	#trigrams = trigram_finder.nbest(TrigramAssocMeasures.chi_sq, 1)
	#print trigrams

	#bag	= [stemmer.stem(x.lower()) for x in list_of_words]
	bag	= [x.lower() for x in list_of_words]
	return set(bag)

def process_tweets(tweets):
	feature_list = []
	for tweet in tweets:
		(tweet_id, text, majority_polarity) = tweet
		#bag = [x for x in fix_tweet_text(text) if x not in classify.STOPWORDS and len(x) > 1]
		bag = [x for x in fix_tweet_text(text) if len(x) > 1]
		feature_list += classify.features(bag, majority_polarity)
	return feature_list

def process_tweet(tweet):
	bag = [x for x in fix_tweet_text(tweet) if x not in classify.STOPWORDS and len(x) > 1]
	fd = dict([(w, True) for w in bag])
	return fd

def process_bigrams(conn, polarity):
	cursor = conn.cursor()
	cursor.execute(Statements.GRAM_SQL % polarity)

	rows = list(cursor.fetchall())
	print rows[0]
	cursor.close()

def update_tweet_polarity(tweet_id, polarity, conn):
	cursor = conn.cursor()
	sql = Statements.UPDATE_AUTO % (polarity, tweet_id)
	cursor.execute(sql)
	conn.commit()
	cursor.close()

def main_function():
	conn = MySQLdb.connect(host=DATABASES['date_cutoff']['HOST'], 
			user=DATABASES['date_cutoff']['USER'], 
			passwd=DATABASES['date_cutoff']['PASSWORD'], 
			db=DATABASES['date_cutoff']['NAME'])

	training_tweets = classify.get_training_tweets(conn_analysis)
	training_feature_set = process_tweets(training_tweets)

	config_megam('/opt/packages')
	classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)

	error_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	count_dict = {'+':0, '-':0, 'I':0, 'O':0} 
	guess_dict = {'+':0, '-':0, 'I':0, 'O':0} 

	full_matrix = {'+':{'+':0, '-':0, 'I':0, 'O':0}, 
				'-':{'+':0, '-':0, 'I':0, 'O':0}, 
				'I':{'+':0, '-':0, 'I':0, 'O':0}, 
				'O':{'+':0, '-':0, 'I':0, 'O':0}}


	test_tweets = classify.get_test_tweets(conn_analysis)
	test_feature_set = process_tweets(test_tweets)

	classifier.show_most_informative_features(10)
	classifier_accuracy = accuracy(classifier, test_feature_set)
	print "classifier accuracy: " + repr(classifier_accuracy)

	#for f in test_tweets:
	#	guess = classifier.classify(process_tweet(f[1]))
	#	full_matrix[f[2]][guess] += 1

	#	if (guess == '-') or (guess == '+'):
	#		update_tweet_polarity(f[0], guess, conn_analysis)
	#print full_matrix


if __name__ == '__main__':
	main_function()
