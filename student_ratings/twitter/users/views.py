import csv

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login 
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Count

from twitter.users.forms import UserLoginForm
from twitter.sentiment.models import Sentiment

def login_user(request):
	error_msg = None
	next_url = request.REQUEST.get('next', '/')

	if request.method == 'POST':
		form = UserLoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					#forward user to where they really need to be. 

					return HttpResponseRedirect(next_url)
				else:
					error_msg = 'The user is not active.'
			else:
				error_msg = 'The username or password is incorrect. Try again.'
	else:
		form = UserLoginForm()

	return render_to_response('users/login.html', 
								{'form':form,
								'next_url':next_url,
								'error_msg':error_msg}, 
								context_instance=RequestContext(request))

def logout_user(request):
	logout(request)
	return render_to_response('index.html', 
		context_instance=RequestContext(request))

@login_required
def user_ratings(request):
	stats = []
	if request.user.is_staff:
			ratings_results = Sentiment.objects.values('user', 'vote').annotate(ratings=Count('user'))
			user_list = Sentiment.objects.values('user').distinct()

			for u in user_list:
				user_id = u['user']

				us = UserStats()
				us.user = User.objects.get(id=user_id)

				total = 0
				for r in ratings_results.filter(user=user_id):
					v = r['vote']

					if (v == '+'):
						us.positive = r['ratings']
						total += us.positive
					elif (v == '-'):
						us.negative = r['ratings']
						total += us.negative
					elif (v == 'I'):
						us.irrelevant = r['ratings']
						total += us.irrelevant
					elif (v == 'O'):
						us.neutral = r['ratings']
						total += us.neutral

				us.total = total
				stats.append(us)	
			
	return render_to_response('users/stats.html', {'stats':stats}, context_instance=RequestContext(request))


def all_user_ratings(request):
	stats = []
	if request.user.is_staff:
		user_list = User.objects.all().distinct().order_by('last_name')

		for u in user_list:
			user_id = u.id

			ratings_results = Sentiment.objects.values('user', 'vote').annotate(ratings=Count('user')).filter(user=u.id)
			us = UserStats()
			us.user = User.objects.get(id=user_id)

			total = 0
			for r in ratings_results:
				v = r['vote']

				if (v == '+'):
					us.positive = r['ratings']
					total += us.positive
				elif (v == '-'):
					us.negative = r['ratings']
					total += us.negative
				elif (v == 'I'):
					us.irrelevant = r['ratings']
					total += us.irrelevant
				elif (v == 'O'):
					us.neutral = r['ratings']
					total += us.neutral

			us.total = total
			stats.append(us)
	return render_to_response('users/stats.html', {'stats':stats}, context_instance=RequestContext(request))

@login_required
def data(request):
	user = request.user
	votes = Sentiment.objects.filter(user=user).order_by('vote_timestamp')

	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=data.csv'

	writer = csv.writer(response)
	writer.writerow(['tweet_id', 'rating', 'timestamp_of_rating', 'country_code', 
						'state_code', 'tweet_year', 'tweet_month', 'tweet_day', 'tweet_hour', 'tweet_weekday'])
	for vote in votes:
		tweeter = vote.tweet.tweeter
		timestamp = vote.tweet.timestamp
		writer.writerow([vote.tweet.id, vote.vote, vote.vote_timestamp, tweeter.country_code, 
				tweeter.state_code, timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.weekday()])
	return response
	
class UserStats:
	""" Class created for passing user-rating statistics to the front end """
	user = None
	negative = 0
	neutral = 0
	positive = 0
	irrelevant = 0
	total = 0
