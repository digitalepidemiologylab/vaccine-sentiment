from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from twitter.sentiment.models import Sentiment

@login_required
def index(request):
	groups = Group.objects.all()
	return render_to_response('stats/index.html', 
				{'groups':groups}, 
				context_instance=RequestContext(request))

@login_required
def users(request):
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

	return render_to_response('stats/users.html', 
				{'stats':stats}, 
				context_instance=RequestContext(request))

def get_stats_for_users(users):
	stats = []

	for u in users:
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
	return stats


@login_required
def groups(request, group_id):
	g = Group.objects.get(id=group_id)
	user_list = g.user_set.all().order_by('last_name')
	stats = get_stats_for_users(user_list)

	return render_to_response('stats/groups.html', 
				{'stats':stats, 
				 'group':g}, 
				context_instance=RequestContext(request))


class UserStats:
	""" Class created for passing user-rating statistics to the front end """
	user = None
	negative = 0
	neutral = 0
	positive = 0
	irrelevant = 0
	total = 0
