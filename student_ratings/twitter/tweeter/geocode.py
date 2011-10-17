import urllib
from django.utils import simplejson as json

YAHOO_APP_ID = 'jMYP1250'
YAHOO_GEOCODER_URL = 'http://where.yahooapis.com/geocode'

def yahoo_geocode(location):
	"Take a location, return the geographical location, if found"
	url_str = urllib.urlencode({
					'appid':YAHOO_APP_ID,
					'flags':'j',
					'q':location, 
				})

	s =  YAHOO_GEOCODER_URL + '?%s' % url_str
	f = urllib.urlopen(s) 
	json_result = json.loads(f.read())

	geocode_results = []

	if json_result['ResultSet']['Found'] > 0:

		for result in json_result['ResultSet']['Results']:
			geocode_result = Geocode()
			geocode_result.country_code = result['countrycode']
			geocode_result.state_code = result['statecode']
			geocode_result.latitude = result['latitude']
			geocode_result.longitude = result['longitude']

			geocode_results.append(geocode_result)

		return geocode_results
	else:
		return None

def yahoo_reverse_geocode(location):
	""" Take a lat/long pair, and return the geographical location """
	url_str = urllib.urlencode({
			'appid':YAHOO_APP_ID,
			'flags':'j',
			'gflags':'R',
			'q':location, 
		})
	
	s = YAHOO_GEOCODER_URL + '?%s' % url_str
	f = urllib.urlopen(s)

	json_result = json.loads(f.read())

	geocode_result = Geocode()

	if json_result['ResultSet']['Found'] == 1:
		if len(json_result['ResultSet']['Results']) > 1:
			geocode_result.ambiguous = True
		else:
			result = json_result['ResultSet']['Results'][0]

			geocode_result.country_code = result['countrycode']
			geocode_result.state_code = result['statecode']
			geocode_result.latitude = result['latitude']
			geocode_result.longitude = result['longitude']
		return geocode_result
	else:
		return None

class Geocode:
	"Class to hold the results of the Geocoding process"
	country_code = None
	state_code = None
	latitude = None
	longitude = None
	country_name = None

	#If there were multiple results returned from the geocoding
	#process, mark this as true. 
	ambiguous = False

	#If there is no consensus between successive geocoding runs, 
	#mark this as true
	no_consensus = False
