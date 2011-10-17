#!/usr/bin/env python 

import csv

f = csv.reader(open('full-data-no-friends-followers-text-fixed.csv'), delimiter=';', quotechar='"');
o = csv.writer(open('locations.csv', 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

for x in f:
	o.writerow([x[1], x[4].replace('\n', '')])
