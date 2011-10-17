#!/usr/bin/env python 

import urllib
import BeautifulSoup as bs 
import csv

def get_weekly_flu(week, column, url):
	''' Scrape the weekly CDC website and extract the data in column 'column' for the week (01 - 52) '''
	content = urllib.urlopen(url % week)
	soup = bs.BeautifulSoup(content)

	data_table = None

	#Get the right table
	for table in soup.findAll('table'):
		caption = table.find('caption')
		if caption:
			try: 
				table_header = caption.find('h3').string
			except AttributeError:
				table_header = caption.find('h6').string
			if 'Regional Summary' in table_header:
				data_table = table
				break

	region_data = {}
	if data_table:
		rows = data_table.findAll('tr')
		for row in rows:
			cols = row.findAll('td')
			if len(cols) > 0:
				try:
					region = cols[0].find('b').string
				except AttributeError:
					region = cols[0].find('strong').string

				data = cols[column].string
				region = region.strip()
				region_data[region] = int(data.replace(',', '') )
	return region_data

def write_data_for_weeks(url, flu_season_weeks, outfile):	
	all_data = {'Weeks':[], 'Nation':[], 'Region 1':[], 'Region 2':[], 'Region 3':[], 
						'Region 4':[], 'Region 5':[], 'Region 6':[], 'Region 7':[], 
						'Region 8':[], 'Region 9':[], 'Region 10':[]}

	for week in flu_season_weeks:
		print "WEEK: " + week
		data = get_weekly_flu(week, 6, url)
		all_data['Weeks'].append(week)

		for key, value in data.items():
			all_data[key].append(value)

	data_writer = csv.writer(open(outfilename, 'w'), delimiter='\t')
	data_writer.writerow(["'Weeks'"] + all_data['Weeks'])

	for region in all_data:
		if region != 'Weeks':
			data_writer.writerow(["'%s'" % region] + all_data[region])

#Data for 2009 - 2010 season (starting at week 40)
flu_season_weeks = ['%02d' % i for i in range(40,53)] + ['%02d' % i for i in range(1,21)]
season_url_2009_2010 = 'http://cdc.gov/flu/weekly/weeklyarchives2009-2010/weekly%s.htm'
outfilename = '2009-2010-season-raw.txt'

write_data_for_weeks(season_url_2009_2010, flu_season_weeks, outfilename)

#2008 - 2009 season (starting at week 34)
flu_season_weeks = ['%02d' % i for i in range(35,40)] 
season_url_2008_2009 = 'http://cdc.gov/flu/weekly/weeklyarchives2008-2009/weekly%s.htm'
outfilename = '2008-2009-season-raw.txt'

write_data_for_weeks(season_url_2008_2009, flu_season_weeks, outfilename)
