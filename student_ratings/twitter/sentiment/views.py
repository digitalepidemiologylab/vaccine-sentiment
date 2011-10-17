from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from twitter.sentiment.models import Sentiment
from twitter.sentiment.models import ControlTweet
from twitter.tweets.models import Tweet
from twitter.tweets.views import random_tweet

def convert_rating(vote):
	if vote == "negative":
		return "-"
	elif vote == "positive":
		return "+"
	elif vote == "irrelevant":
		return "I"
	else:
		return "O"

@login_required
def rate(request):
	if request.method == 'POST':
		user = request.user
		vote = request.POST['rating']
		voted_tweet_id = request.POST['tweet_id']
		tweet = Tweet.objects.get(tweet_id=voted_tweet_id)

		#Users can't vote twice
		existing_sentiments = Sentiment.objects.filter(user=user, tweet=tweet)
		if not existing_sentiments:
			sentiment = Sentiment()
			sentiment.user = user
			sentiment.vote = convert_rating(vote)
			sentiment.tweet = tweet

			sentiment.save()

			tweet_type = request.POST['tweet_type']
			if tweet_type == "control":
				ControlTweet.objects.update_control_tweet(user, tweet.ordinal)

	return HttpResponseRedirect(reverse(random_tweet))

@login_required
def redo_previous(request):
	""" Redo the last vote """
	u = request.user

	if request.method == 'POST':
		vote = request.POST['rating']
		tweet = Tweet.objects.get(tweet_id=request.POST['tweet_id'])
		
		#update rating of last tweet
		existing_sentiment = Sentiment.objects.filter(user=u, tweet=tweet)[0]
		if existing_sentiment:
			existing_sentiment.vote = convert_rating(vote)
			existing_sentiment.save()

		return HttpResponseRedirect(reverse(random_tweet))
	else:
		last_sentiment = Sentiment.objects.filter(user=u).order_by('-vote_timestamp')[:1][0]
		return render_to_response('tweets/redo.html', 
				{'sentiment':last_sentiment}, 
				context_instance=RequestContext(request))
