from django.db import models
from django.contrib.auth.models import User

from twitter.tweets.models import Tweet
from twitter.sentiment.managers import ControlTweetManager

SENTIMENT_CHOICES = (
	('+', 'Positive'),
	('-', 'Negative'),
	('O', 'Neutral'),
	('I', 'Irrelevant'),
)

class Sentiment(models.Model):
	user = models.ForeignKey(User)
	tweet = models.ForeignKey(Tweet)
	vote = models.CharField(max_length=1, choices=SENTIMENT_CHOICES, blank=True, null=False)
	vote_timestamp = models.DateTimeField(null=False, auto_now=True)

class ControlTweet(models.Model):
	user = models.ForeignKey(User, unique=True)
	last_control_ordinal = models.BigIntegerField(blank=True, null=False)

	objects = ControlTweetManager()

#The consensus of sentiment for each tweet.
class SentimentConsensus(models.Model):
	tweet = models.ForeignKey(Tweet)
	majority_vote = models.CharField(max_length=1, choices=SENTIMENT_CHOICES, blank=True, null=True)
	#The percentage of people that agreed on the majority (expressed as a number between 0 and 1)
	majority_percentage =  models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
	no_consensus = models.BooleanField(default=True)
