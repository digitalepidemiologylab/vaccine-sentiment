from django.contrib import admin

from twitter.users.models import UserProfile

admin.site.register(UserProfile)
