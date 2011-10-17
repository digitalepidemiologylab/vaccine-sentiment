/* This SQL query used to generate a file of training tweets for Lingpipe. */

SELECT sc.tweet_id, sc.majority_vote, tt.text FROM sentiment_sentimentconsensus sc, tweets_tweet tt
WHERE sc.num_votes < 3 AND sc.tweet_id=tt.id;
