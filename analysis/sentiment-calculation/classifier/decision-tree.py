#!/usr/bin/env python 

#We tried using a simple decision tree classifier. 

import MySQLdb
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk import config_megam
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.classify import DecisionTreeClassifier
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import TrigramAssocMeasures
from nltk.classify import accuracy 
from nltk.stem import PorterStemmer

import string

#We need to customize the standard stop words
#STOPWORDS = stopwords.words('english')
#STOPWORDS.remove('not')
#STOPWORDS.remove('no')
STOPWORDS = []

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
	GRAM_SQL += "AND sc.num_votes > 2 AND majority_vote = '%s' AND majority_percentage > 0.75" 

	UPDATE_AUTO = "UPDATE sentiment_sentimentconsensus SET auto_classified=1, "
	UPDATE_AUTO += "auto_vote='%s' WHERE tweet_id=%s"

def fix_tweet_text(text):
	stemmer = PorterStemmer()
	list_of_words = text.split()

	#bigram_finder = BigramCollocationFinder.from_words(list_of_words)
	#bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, 50)

	#print "BIGRAMS"
	#print bigrams
	bag	= [stemmer.stem(x.lower()) for x in list_of_words]
	#bag	= [x.lower() for x in list_of_words]

	#for bt in bigrams:
	#j	x = "%s %s" % (bt[0].lower(), bt[1].lower())
	#	bag.append(x)

	#trigram_finder = TrigramCollocationFinder.from_words(list_of_words)
	#trigrams = trigram_finder.nbest(TrigramAssocMeasures.chi_sq, 1)
	return bag

def process_tweets(tweets):
	feature_list = []
	for tweet in tweets:
		(tweet_id, text, majority_polarity) = tweet
		bag = [x for x in fix_tweet_text(text) if x not in STOPWORDS and len(x) > 1]
		feature_list += features(bag, majority_polarity)
	return feature_list

def process_tweet(tweet):
	bag = [x for x in fix_tweet_text(tweet) if x not in STOPWORDS and len(x) > 1]
	fd = dict([(w, True) for w in bag])
	return fd

def process_bigrams(conn, polarity):
	cursor = conn.cursor()
	sql = Statements.GRAM_SQL % polarity
	cursor.execute(sql)

	rows = list(cursor.fetchall())
	l = [x[0] for x in rows]
	words_split = map(string.split, l)
	words = [item for sublist in words_split for item in sublist]

	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_freq_filter(3)
	bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, 10)

	bigram_list = []
	for bt in bigrams:
		x = "%s %s" % (bt[0].lower(), bt[1].lower())
		bigram_list.append(x)

	bigram_features = features(bigram_list, polarity)
	return bigram_features
	cursor.close()

def features(words, sense):
	fd = dict([(word, True) for word in words])
	if (sense == 'I') or (sense == 'O'):
		return [(fd, 'E')]
	else:
		return [(fd, sense)]

def get_training_tweets(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.NO_MIN_SQL)

	rows = list(cursor.fetchall())
	return rows

	cursor.close()

def get_test_tweets(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.SINGLE_VOTE_SQL_ALL)

	rows = list(cursor.fetchall())

	return rows
	cursor.close()

def update_tweet_polarity(tweet_id, polarity, conn):
	cursor = conn.cursor()
	sql = Statements.UPDATE_AUTO % (polarity, tweet_id)
	cursor.execute(sql)
	conn.commit()
	cursor.close()

def main_function():
	conn = MySQLdb.connect(host="localhost", user="root", passwd="tanzania", db="twitter_analysis")
	hq_conn = MySQLdb.connect(host="localhost", user="root", passwd="tanzania", db="twitter")

	training_tweets = get_test_tweets(conn)
	training_feature_set = process_tweets(training_tweets)

	classifier = DecisionTreeClassifier.train(training_feature_set)

	test_tweets = get_training_tweets(conn)
	test_feature_set = process_tweets(test_tweets)

	classifier_accuracy = accuracy(classifier, test_feature_set)

	alt_full_matrix = {'+':{'+':0, '-':0, 'E':0}, 
				'-':{'+':0, '-':0, 'E':0}, 
				'E':{'+':0, '-':0, 'E':0}}

	#for f in test_tweets:
	#f = test_tweets[0]

	#print f
	#guess = classifier.classify(process_tweet(f[1]))
	#print guess
	#	update_tweet_polarity(f[0], guess, conn)
	##	pl = classifier.prob_classify(process_tweet(f[1]))
	#	idx = f[2]
	#	if idx == 'I' or idx == 'O':
	#		idx = 'E'
	#	alt_full_matrix[idx][guess] += 1

	#print alt_full_matrix

	print "classifier accuracy: " + repr(classifier_accuracy)

if __name__ == '__main__':
	main_function()
