from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Count

from django.contrib.auth.decorators import login_required

from twitter.tweets.models import Tweet
from twitter.sentiment.models import Sentiment
from twitter.sentiment.models import ControlTweet
from twitter.users.models import UserProfile

def index(request):
	if request.user.is_authenticated():
		num_ratings = Sentiment.objects.filter(user=request.user).count()
		print "RATING" + repr(num_ratings)
		if num_ratings > 1499:
			return render_to_response('index.html', 
					{'data':True}, context_instance=RequestContext(request))

	return render_to_response('index.html', {}, context_instance=RequestContext(request))

@login_required
def random_tweet(request):

	user = request.user
	num_ratings = Sentiment.objects.filter(user=user).count()
	tweet, tweet_type = get_tweet(user, num_ratings)

	return render_to_response('tweets/random.html', 
			{'tweet': tweet,
			'num_ratings':num_ratings,
			'tweet_type':tweet_type},
			context_instance=RequestContext(request))

def get_tweet(user, num_ratings):
	""" Returns a random tweet or a control tweet, based on the number of 
	ratings by the user. Essentially returns a control tweet to the user 
	every other time. """

	tweet_type = "random"

	random_always = False

	try:
		profile = UserProfile.objects.get(user=user)
		random_always = profile.random_only
	except ObjectDoesNotExist:
		random_always = False

	if ((num_ratings % 2) or random_always):
		tweet = get_random_tweet(user)
	else:
		tweet_type = "control"
		tweet = get_control_tweet(user)

	return (tweet, tweet_type)

def get_random_tweet(user):
	""" Returns a random tweet that hasn't already been rated by user"""
	found = False;
	tweet = None;

	while not found:
		next_ordinal = randint(1, Ordinal.MAX_ORDINAL)

		try: 
			tweet = Tweet.objects.get(ordinal=next_ordinal)
		except ObjectDoesNotExist:
			return None

		existing_sentiments = Sentiment.objects.filter(user=user, tweet=tweet)
		if not existing_sentiments:
			found = True
	return tweet

def get_control_tweet(user):
	""" Returns the next control tweet that hasn't already been rated by the user"""
	control_tweets = ControlTweet.objects.filter(user=user)

	next_ordinal = 0

	if control_tweets:
		control_tweet = control_tweets[0]
		next_ordinal = control_tweet.last_control_ordinal
	
	found = False
	while not found and next_ordinal < Ordinal.MAX_ORDINAL:
		next_ordinal += 1	
		tweet = Tweet.objects.get(ordinal=next_ordinal)
		existing_sentiments = Sentiment.objects.filter(user=user, tweet=tweet)
		if not existing_sentiments:
			found = True

	if next_ordinal >= Ordinal.MAX_ORDINAL:
		return None;
	return tweet

def view_tweet(request, tweet_id):
	tweet = get_object_or_404(Tweet, pk=tweet_id)

	votes_summary =  Sentiment.objects.filter(tweet=tweet).values('vote').annotate(total=Count('vote'))

	return render_to_response('tweets/display.html', 
			{'tweet': tweet,
			'votes_summary':votes_summary},
			context_instance=RequestContext(request))

class Ordinal:
	MAX_ORDINAL = 477768
