#!/usr/bin/env python 

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


from nltk.probability import FreqDist, ConditionalFreqDist
import string
from database_settings import DATABASES

#We need to customize the standard stop words
STOPWORDS = stopwords.words('english')
STOPWORDS.remove('not')
STOPWORDS.remove('no')
#STOPWORDS = []

best_words = set()

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
	GRAM_SQL += "AND sc.num_votes > 2 AND majority_vote = '%s'" 

	ALL_TWEETS = "SELECT tt.text from tweets_tweet tt, sentiment_sentimentconsensus sc WHERE sc.tweet_id = tt.id "
	ALL_TWEETS += "AND sc.num_votes > 2" 

	UPDATE_AUTO = "UPDATE sentiment_sentimentconsensus SET auto_classified=1, "
	UPDATE_AUTO += "auto_vote='%s' WHERE tweet_id=%s"

def fix_tweet_text(text):
	stemmer = PorterStemmer()
	list_of_words = text.split()
	bag	= [x.lower() for x in list_of_words if x in best_words]
	return bag

def process_tweets(tweets):
	feature_list = []
	for tweet in tweets:
		(tweet_id, text, majority_polarity) = tweet
		bag = [x for x in fix_tweet_text(text) if x not in STOPWORDS and len(x) > 1]
		feature_list += features(bag, majority_polarity)

		list_of_words = [x for x in text.split() if x not in STOPWORDS and len(x) > 1 and not (x.startswith('http://'))]
		bigram_finder = BigramCollocationFinder.from_words(list_of_words)
		bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, 5)

		bigram_list = []
		for bt in bigrams:
			x = "%s %s" % (bt[0].lower(), bt[1].lower())
			bigram_list.append(x)

		bigram_features = features(bigram_list, majority_polarity)
		feature_list += bigram_features
	return feature_list

def process_tweet(tweet):
	bag = [x for x in fix_tweet_text(tweet) if x not in STOPWORDS and len(x) > 1]

	list_of_words = [x for x in tweet.split() if x not in STOPWORDS and len(x) > 1 and not (x.startswith('http://'))]
	bigram_finder = BigramCollocationFinder.from_words(list_of_words)
	bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, 5)

	bigram_list = []
	for bt in bigrams:
		x = "%s %s" % (bt[0].lower(), bt[1].lower())
		bag.append(x)

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

	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_freq_filter(4)
	bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, 10)

	bigram_list = []
	for bt in bigrams:
		x = "%s %s" % (bt[0].lower(), bt[1].lower())
		bigram_list.append(x)

	bigram_features = features(bigram_list, polarity)
	best_features += bigram_features
	return best_features
	cursor.close()

def features(words, sense):
	fd = dict([(word, True) for word in words])
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
	conn = MySQLdb.connect(host=DATABASES['date_cutoff']['HOST'], 
			user=DATABASES['date_cutoff']['USER'], 
			passwd=DATABASES['date_cutoff']['PASSWORD'], 
			db=DATABASES['date_cutoff']['NAME'])

	training_tweets = get_test_tweets(conn)
	#training_feature_set = process_tweets(training_tweets)

	total_word_count = total_words(conn)
	training_feature_set = process_bigrams(conn, '+', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, '-', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, 'I', total_word_count, best_words)
	training_feature_set += process_bigrams(conn, 'O', total_word_count, best_words)


	print "configuring megam"
	config_megam('/opt/packages')
	print "starting training"
	classifier = MaxentClassifier.train(training_feature_set, algorithm="megam", trace=0)
	print "starting end training"
	classifier.show_most_informative_features(40)

	test_tweets = get_training_tweets(conn)
	test_feature_set = process_tweets(test_tweets)

	classifier_accuracy = accuracy(classifier, test_feature_set)

	#full_matrix = {'+':{'+':0, '-':0, 'I':0, 'O':0}, 
	#			'-':{'+':0, '-':0, 'I':0, 'O':0}, 
	#			'I':{'+':0, '-':0, 'I':0, 'O':0}, 
	#			'O':{'+':0, '-':0, 'I':0, 'O':0}}

	#for f in test_tweets:
	#	guess = classifier.classify(process_tweet(f[1]))
	#	full_matrix[f[2]][guess] += 1

	#print full_matrix
	print "classifier accuracy: " + repr(classifier_accuracy)

if __name__ == '__main__':
	main_function()
