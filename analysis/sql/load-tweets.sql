LOAD DATA LOCAL INFILE '/tmp/quotes-fixed-squished-short.csv' INTO TABLE tweets_tweet FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' (tweet_id, text);
