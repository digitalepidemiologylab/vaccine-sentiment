from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from twitter.tweeter.models import Tweeter
from twitter.tweeter.models import Country

#smart_str fixes unicode issues in the location strings. 
from django.utils.encoding import smart_str, smart_unicode

import geocode

@login_required
@permission_required('tweeter.can_geocode', login_url='/')
def random_tweeter(request):
	tweeter = Tweeter.objects.filter(unknown_location=True, 
					ambiguous_location=False, 
					location_string__isnull=False, 
					human_geocoder__isnull=True).order_by("?")[0]

	num_geocoded = Tweeter.objects.filter(human_geocoder=request.user).count()

	num_left = Tweeter.objects.filter(unknown_location=True, 
						ambiguous_location=False, 
						location_string__isnull=False, 
						human_geocoder__isnull=True).count()

	return render_to_response('tweeter/random.html', 
			{'tweeter':tweeter, 
			'num_left':num_left,
			'num_geocoded':num_geocoded}, 
			context_instance=RequestContext(request))

@login_required
@permission_required('tweeter.can_geocode', login_url='/')
def geocode_location(request):
	""" Send the string to the geocoder, or just skip to the next available tweeter (based on the form input) """
	if request.method == 'POST':
		tweeter_id = request.POST['tweeter_id']
		tweeter = Tweeter.objects.filter(id=tweeter_id)[0]

		if 'geocode' in request.POST:
			location_string = tweeter.location_string.strip()

			alt_location = None
			if 'alt-location' in request.POST:
				if len(request.POST['alt-location']) > 0:
					#user has provided an alternate location string
					location_string = request.POST['alt-location'].strip()
					alt_location = location_string

			geocode_results = geocode.yahoo_geocode(smart_str(location_string))

			if geocode_results:
				for gr in geocode_results:
					try:
						country = Country.objects.get(country_code = gr.country_code)
						gr.country_name = country.country_name
					except Country.DoesNotExist:
						gr.country_name = None


			location_string = smart_str(tweeter.location_string)
			return render_to_response('tweeter/confirm.html', 
						{'tweeter':tweeter, 
						'location_string':location_string,
						'alt_location':alt_location,
						'geocode_results':geocode_results}, 
						context_instance=RequestContext(request))
		elif 'no-location' in request.POST:
			tweeter.unknown_location = True
			tweeter.ambiguous_location = False;
			tweeter.human_geocoder = request.user
			tweeter.save()
			#we'll need to do something here
			return HttpResponseRedirect("/tweeter/locate")

		return HttpResponseRedirect("/tweeter/locate/")

@login_required
@permission_required('tweeter.can_geocode', login_url='/')
def confirm(request):
	if request.method == 'POST':
		tweeter_id = request.POST['tweeter_id']
		tweeter = Tweeter.objects.filter(id=tweeter_id)[0]

		if 'accept' in request.POST:
			#one of the locations has been accepted
			tweeter.unknown_location = False
			tweeter.ambiguous_location = False
			tweeter.country_code = request.POST['country_code']
			tweeter.state_code = request.POST['state_code']
			tweeter.human_geocoder = request.user
			tweeter.save()
		elif 'reject' in request.POST:
			#user can't determine the location
			tweeter.unknown_location = True
			tweeter.ambiguous_location = False
			tweeter.human_geocoder = request.user
			tweeter.save()
		elif 'ambiguous' in request.POST:
			#the location string resolves to multiple locations, user can't pick 
			#between those
			tweeter.unknown_location = True
			tweeter.ambiguous_location = True
			tweeter.human_geocoder = request.user
			tweeter.save()

	#always want to show a new location
	return HttpResponseRedirect("/tweeter/locate")
