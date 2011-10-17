#!/usr/bin/env python 

#From the full dataset, extract the user name and the twitter user id. 
#The users.csv file will be sorted, uniqued and then slurped into a database. 

import csv

f = csv.reader(open('full-data-no-friends-followers-text-fixed.csv'), delimiter=';', quotechar='"');
o = csv.writer(open('users.csv', 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

for x in f:
	o.writerow([x[1], x[5].replace('\n', '')])
