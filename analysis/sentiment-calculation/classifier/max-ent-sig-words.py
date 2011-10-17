#!/usr/bin/env python 

# This method from 
# streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/ 

# We train the classifier with the most significant words (the highest information features). 
# We use the top 600 words for each polarity where significance is defined by how common that word is 
# within tweets of a particular polarity, compared to tweets of other polarities. 
import classify

from nltk import word_tokenize
from nltk import config_megam
from nltk.classify import MaxentClassifier
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import TrigramAssocMeasures
from nltk.classify import accuracy 
from nltk.probability import FreqDist, ConditionalFreqDist

import MySQLdb
import string
from database_settings import DATABASES

STOPWORDS = classify.STOPWORDS
best_words = set()

class Statements:
	GRAM_SQL = "SELECT tt.text from tweets_tweet tt, sentiment_sentimentconsensus sc WHERE sc.tweet_id = tt.id "
	GRAM_SQL += "AND sc.num_votes < 3 AND majority_vote = '%s'" 

	ALL_TWEETS = "SELECT tt.text from tweets_tweet tt, sentiment_sentimentconsensus sc WHERE sc.tweet_id = tt.id "
	ALL_TWEETS += "AND sc.num_votes < 3" 

	UPDATE_AUTO = "UPDATE sentiment_sentimentconsensus SET auto_classified=1, "
	UPDATE_AUTO += "auto_vote='%s' WHERE tweet_id=%s"

def fix_tweet_text(text):
	# Then for each tweet, the feature set is the words in the tweet that are also in the 
	# set of most significant words (best_words)
	list_of_words = text.split()
	bag	= [x.lower() for x in list_of_words if x in best_words]
	print bag
	return bag

def process_tweets(tweets):
	feature_list = []
	for tweet in tweets:
		(tweet_id, text, majority_polarity) = tweet
		bag = [x for x in fix_tweet_text(text) if x not in STOPWORDS and len(x) > 1]
		#bag = [x for x in fix_tweet_text(text) if len(x) > 1]
		feature_list += features(bag, majority_polarity)
	return feature_list

def process_tweet(tweet):
	bag = [x for x in fix_tweet_text(tweet) if x not in STOPWORDS and len(x) > 1]
	fd = dict([(w, True) for w in bag])
	return fd

def total_words(conn):
	cursor = conn.cursor()
	cursor.execute(Statements.ALL_TWEETS)

	rows = list(cursor.fetchall())
	l = [x[0] for x in rows]
	words_split = map(string.split, l)
	words = [item for sublist in words_split for item in sublist]
	return len(words)

	cursor.close()

def process_bigrams(conn, polarity, total_word_count, best_words):
	cursor = conn.cursor()
	sql = Statements.GRAM_SQL % polarity
	cursor.execute(sql)

	rows = list(cursor.fetchall())
	l = [x[0] for x in rows]
	words_split = map(string.split, l)
	raw_words = [item for sublist in words_split for item in sublist]

	words = []
	for w in raw_words:
		if not (w.startswith("http://") or w.startswith("@")):
			words.append(w)

	word_fd = FreqDist()
	label_word_fd = ConditionalFreqDist()

	for word in words:
		word_fd.inc(word.lower())
		label_word_fd[polarity].inc(word.lower())

	pos_word_count = label_word_fd[polarity].N()

	word_scores = {}

	for word,freq in word_fd.iteritems():
		score =  BigramAssocMeasures.chi_sq(label_word_fd[polarity][word], (freq, pos_word_count), total_word_count)
		word_scores[word]  = score

	best_raw = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:600]
	best = [x[0] for x in best_raw if x[0] not in STOPWORDS and len(x[0]) > 1]
	best_words.update(best)
	best_features = features(best, polarity)
	return best_features
	cursor.close()

def features(words, sense):
	fd = dict([(word, True) for word in words])
	return [(fd, sense)]

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

	total_word_count = total_words(conn)
	training_feature_set = process_bigrams(conn, '+', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, '-', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, 'I', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, 'O', total_word_count, best_words)

	config_megam('/opt/packages')
	#classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)
	classifier = NaiveBayesClassifier.train(training_feature_set)
	classifier.show_most_informative_features(10)

	test_tweets = classify.get_test_tweets(conn)
	test_feature_set = process_tweets(test_tweets)

	classifier_accuracy = accuracy(classifier, test_feature_set)

	print "classifier accuracy: " + repr(classifier_accuracy)

if __name__ == '__main__':
	main_function()
