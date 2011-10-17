from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string

#We need to customize the standard stop words
LUCENE_STOPWORDS = ["a", "and", "are", "as", "at", "be", "but", "by",  "for",
"if", "in", "into", "is", "it", "no", "not", "of", "on", "or", "s", "such",
"t", "that", "the", "their", "then", "there", "these", "they", "this", "to",
"was", "will", "with"]

STOPWORDS = LUCENE_STOPWORDS
STOPWORDS.remove('not')
STOPWORDS.remove('no')

#STOPWORDS = stopwords.words('english')
#STOPWORDS.remove('against')

class Statements:
	HUMAN_RATED_SQL = "SELECT sc.tweet_id, tt.text, sc.majority_vote " 
	HUMAN_RATED_SQL += "FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	HUMAN_RATED_SQL += "WHERE sc.tweet_id=tt.id AND majority_vote IS NOT NULL "

	TWEETS_TO_CLASSIFY = "SELECT id from tweets_tweet"

	TEST_TWEETS = "SELECT sc.tweet_id, tt.text, sc.majority_vote " 
	TEST_TWEETS += "FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	TEST_TWEETS += "WHERE sc.tweet_id = tt.id AND sc.num_votes > 43 AND test_tweet = true"

	TRAINING_TWEETS = "SELECT sc.tweet_id, tt.text, sc.majority_vote "
	TRAINING_TWEETS +=  "FROM sentiment_sentimentconsensus sc, tweets_tweet tt "
	TRAINING_TWEETS += "WHERE sc.num_votes < 44 and sc.tweet_id = tt.id" 

	TWEET_TEXT = "SELECT text from tweets_tweet WHERE id=%s"

	GRAM_SQL = "SELECT tt.text from tweets_tweet tt, sentiment_sentimentconsensus sc WHERE sc.tweet_id = tt.id "
	GRAM_SQL += "AND sc.num_votes < 3 AND majority_vote = '%s'" 

	UPDATE_AUTO = "UPDATE sentiment_sentimentconsensus SET auto_classified=1, "
	UPDATE_AUTO += "auto_vote='%s' WHERE tweet_id=%s"

	CHECK_CONSENSUS = "SELECT auto_vote from sentiment_sentimentconsensus where tweet_id=%s"
	CHECK_MAJORITY = "SELECT majority_vote from sentiment_sentimentconsensus where tweet_id=%s"

	INSERT_AUTO = "INSERT INTO sentiment_sentimentconsensus (tweet_id, auto_classified, auto_vote) "
	INSERT_AUTO += " VALUES (%s, 1, '%s')"

	UPDATE_NOT_CLASSIFIED = "UPDATE sentiment_sentimentconsensus SET auto_classified=0, auto_vote=NULL "
	UPDATE_NOT_CLASSIFIED += "WHERE tweet_id=%s"

	UPDATE_MANUAL_CLASSIFIED = "UPDATE sentiment_sentimentconsensus SET auto_classified=0,"
	UPDATE_MANUAL_CLASSIFIED += " auto_vote = majority_vote WHERE test_tweet = true"

def update_tweet_polarity(tweet_id, polarity, conn):
	cursor = conn.cursor()

	sql = Statements.CHECK_CONSENSUS % tweet_id
	cursor.execute(sql)
	result = cursor.fetchall()

	if len(result) > 0:
		sql = Statements.UPDATE_AUTO % (polarity, tweet_id)
	else:
		sql = Statements.INSERT_AUTO % (tweet_id, polarity)

	conn.commit()
	cursor.close()

	update_cursor = conn.cursor()
	update_cursor.execute(sql)

	conn.commit()
	update_cursor.close()

def remove_punctuation(punctuated):
	return punctuated.translate(string.maketrans("",""), string.punctuation.replace("!", ""))

def fix_tweet_text(text):
	stemmer = PorterStemmer()
	list_of_words = text.split()
	bag	= [stemmer.stem(remove_punctuation(x.lower())) for x in list_of_words]
	#bag	= [remove_punctuation(x.lower()) for x in list_of_words]
	#no_http_bag = [x for x in bag if not x.startswith("http")]
	#bag	= [stemmer.stem(x.lower()) for x in list_of_words]
	#bag	= [x.lower() for x in list_of_words]
	word_set = set(bag)
	return word_set
	#return bag

def process_tweets(tweets):
	feature_list = []
	for tweet in tweets:
		(tweet_id, text, majority_polarity) = tweet
		bag = [x for x in fix_tweet_text(text) if x not in STOPWORDS and len(x) > 1]
		#bag = [x for x in fix_tweet_text(text) if x not in STOPWORDS]
		#bag = [x for x in fix_tweet_text(text) if len(x) > 1]
		#bag = [x for x in fix_tweet_text(text)]

		#if majority_polarity in ['+', '-']:
		#	majority_polarity = 'U'
		#else:
		#	majority_polarity = 'C'

		feature_list += features(bag, majority_polarity)
	return feature_list

def process_tweet(tweet):
	bag = [x for x in fix_tweet_text(tweet) if x not in STOPWORDS and len(x) > 1]
	fd = dict([(w, True) for w in bag])
	return fd

def features(words, sense):
	fd = dict([(word, True) for word in words])
	return [(fd, sense)]

def get_tweets_to_classify(conn):
	return run_sql(conn, Statements.TWEETS_TO_CLASSIFY)

def run_sql(conn, sql):
	cursor = conn.cursor()
	cursor.execute(sql)
	rows = list(cursor.fetchall())
	cursor.close()
	return rows

def get_tweet_text(conn, tweet_id):
	cursor = conn.cursor()
	sql = Statements.TWEET_TEXT % tweet_id
	cursor.execute(sql)
	return cursor.fetchall()
	cursor.close()

def get_test_tweets(conn):
	return run_sql(conn, Statements.TEST_TWEETS)

def get_training_tweets(conn):
	return run_sql(conn, Statements.TRAINING_TWEETS)
