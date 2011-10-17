from django.db import models

from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User)

	#If True, we'll only show this user random tweets (no control tweets)
	random_only = models.BooleanField(default=False, blank=False, null=False)


