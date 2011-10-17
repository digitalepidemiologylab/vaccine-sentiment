LOAD DATA LOCAL INFILE '/tmp/users-unique.csv' INTO TABLE tweeter_tweeter FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\r\n' (user_name, twitter_user_id)
