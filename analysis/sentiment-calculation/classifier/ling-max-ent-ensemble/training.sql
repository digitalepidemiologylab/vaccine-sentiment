SELECT sc.tweet_id, tt.majority_vote, tt.text 
FROM sentiment_sentimentconsensus sc, tweets_tweet tt
WHERE sc.tweet_id = tt.id AND majority_vote is NOT NULL
