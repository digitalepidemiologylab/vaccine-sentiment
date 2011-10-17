from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'twitter.tweets.views.index'),
	(r'^tweets/$', 'twitter.tweets.views.index'),
	(r'^tweets/rate/', 'twitter.tweets.views.random_tweet'),
	(r'^tweets/view/(?P<tweet_id>\d+)/', 'twitter.tweets.views.view_tweet'),
	(r'^sentiment/rate/', 'twitter.sentiment.views.rate'),
	(r'^sentiment/redo/', 'twitter.sentiment.views.redo_previous'),
	(r'^users/login/', 'twitter.users.views.login_user'),
	(r'^users/logout/', 'twitter.users.views.logout_user'),
	(r'^users/stats/', 'twitter.users.views.all_user_ratings'),
	(r'^user/data/', 'twitter.users.views.data'),
	(r'^stats/groups/(?P<group_id>\d+)/', 'twitter.stats.views.groups'),
	(r'^stats/users/', 'twitter.stats.views.users'),
	(r'^stats/', 'twitter.stats.views.index'),
	(r'^tweeter/locate/', 'twitter.tweeter.views.random_tweeter'),
	(r'^tweeter/geocode/confirm/', 'twitter.tweeter.views.confirm'),
	(r'^tweeter/geocode/', 'twitter.tweeter.views.geocode_location'),
    # Example:
    # (r'^twitter/', include('twitter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('', url(r'^%s(?P<path>.*)/$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}))
