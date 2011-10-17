LOAD DATA LOCAL INFILE '/tmp/countries.txt' INTO TABLE tweeter_country FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' (country_name, country_code)

