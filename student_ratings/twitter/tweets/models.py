from django.db import models

from twitter.tweeter.models import Tweeter

#A model that represents a tweet. 
class Tweet(models.Model):
	tweet_id = models.BigIntegerField(unique=True, blank=False)
	text = models.CharField(max_length=280, blank=False)
	ordinal = models.BigIntegerField(blank=True, null=True)
	tweeter = models.ForeignKey(Tweeter, blank=True, null=True)
	#The date and time this was tweeted. 
	timestamp = models.DateTimeField(null=True)
