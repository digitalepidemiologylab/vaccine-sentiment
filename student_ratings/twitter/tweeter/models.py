from django.db import models
from django.contrib.auth.models import User

class Tweeter(models.Model):
	user_name = models.CharField(max_length=50, blank=False, null=False)
	twitter_user_id = models.IntegerField(blank=False, null=False)
	location_string =  models.CharField(max_length=256, blank=True, null=True)
	country_code = models.CharField(max_length=3, blank=True, null=True)
	state_code =  models.CharField(max_length=3, blank=True, null=True)
	unknown_location = models.BooleanField(default=False)
	ambiguous_location = models.BooleanField(default=False)
	location_count = models.IntegerField(default=0)
	human_geocoder = models.ForeignKey(User, blank=True, null=True)

	class Meta:
		permissions = (
			("can_geocode","Can geocode locations"),)

class Country(models.Model):
	country_name = models.CharField(max_length=512, blank=True, null=False)
	country_code = models.CharField(max_length=3, blank=True, null=False)
