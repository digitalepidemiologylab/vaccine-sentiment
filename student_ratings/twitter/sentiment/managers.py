from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class ControlTweetManager(models.Manager):

	def update_control_tweet(self, user, last_ordinal):
		""" Update an existing control tweet entry, or create a new one. 
		There should be only one control tweet entry per user. """

		try: 
			control_tweet = self.get(user=user)
			control_tweet.last_control_ordinal = last_ordinal
			control_tweet.save()
		except ObjectDoesNotExist:
			control_tweet = self.model()
			control_tweet.user = user
			control_tweet.last_control_ordinal = last_ordinal
			control_tweet.save()
