from django.contrib.auth.decorators import login_required
from forum.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.utils.http import urlquote_plus
from django.utils.html import strip_tags
from django.utils import simplejson
from django.core.urlresolvers import reverse
from forum.forms import *
from forum.utils.html import sanitize_html
from forum.authentication import user_updated
import decorators

import time

USERS_PAGE_SIZE = 35# refactor - move to some constants file

def users(request):
    is_paginated = True
    sortby = request.GET.get('sort', 'reputation')
    suser = request.REQUEST.get('q',  "")
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    if suser == "":
        if sortby == "newest":
            objects_list = Paginator(User.objects.all().order_by('-date_joined'), USERS_PAGE_SIZE)
        elif sortby == "last":
            objects_list = Paginator(User.objects.all().order_by('date_joined'), USERS_PAGE_SIZE)
        elif sortby == "user":
            objects_list = Paginator(User.objects.all().order_by('username'), USERS_PAGE_SIZE)
        # default
        else:
            objects_list = Paginator(User.objects.all().order_by('-reputation'), USERS_PAGE_SIZE)
        base_url = reverse('users') + '?sort=%s&' % sortby
    else:
        sortby = "reputation"
        objects_list = Paginator(User.objects.filter(username__icontains=suser).order_by('-reputation'), USERS_PAGE_SIZE)
        base_url = reverse('users') + '?name=%s&sort=%s&' % (suser, sortby)

    try:
        users = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        users = objects_list.page(objects_list.num_pages)

    return render_to_response('users/users.html', {
                                "users" : users,
                                "suser" : suser,
                                "keywords" : suser,
                                "tab_id" : sortby,
                                "context" : {
                                    'is_paginated' : is_paginated,
                                    'pages': objects_list.num_pages,
                                    'page': page,
                                    'has_previous': users.has_previous(),
                                    'has_next': users.has_next(),
                                    'previous': users.previous_page_number(),
                                    'next': users.next_page_number(),
                                    'base_url' : base_url
                                }

                                }, context_instance=RequestContext(request))

@login_required
def moderate_user(request, id):
    """ajax handler of user moderation
    """
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404
    if not request.is_ajax():
        return HttpResponseForbidden(mimetype="application/json")

    user = get_object_or_404(User, id=id)
    form = ModerateUserForm(request.POST, instance=user)

    if form.is_valid():
        form.save()
        logging.debug('data saved')
        response = HttpResponse(simplejson.dumps(''), mimetype="application/json")
    else:
        response = HttpResponseForbidden(mimetype="application/json")
    return response

def set_new_email(user, new_email, nomessage=False):
    if new_email != user.email:
        user.email = new_email
        user.email_isvalid = False
        user.save()
        #if settings.EMAIL_VALIDATION == 'on':
        #    send_new_email_key(user,nomessage=nomessage)    

@login_required
def edit_user(request, id):
    user = get_object_or_404(User, id=id)
    if request.user != user:
        raise Http404
    if request.method == "POST":
        form = EditUserForm(user, request.POST)
        if form.is_valid():
            new_email = sanitize_html(form.cleaned_data['email'])

            set_new_email(user, new_email)

            #user.username = sanitize_html(form.cleaned_data['username'])
            user.real_name = sanitize_html(form.cleaned_data['realname'])
            user.website = sanitize_html(form.cleaned_data['website'])
            user.location = sanitize_html(form.cleaned_data['city'])
            user.date_of_birth = sanitize_html(form.cleaned_data['birthday'])
            if len(user.date_of_birth) == 0:
                user.date_of_birth = '1900-01-01'
            user.about = sanitize_html(form.cleaned_data['about'])

            user.save()
            # send user updated signal if full fields have been updated
            if user.email and user.real_name and user.website and user.location and \
                user.date_of_birth and user.about:
                user_updated.send(sender=user.__class__, instance=user, updated_by=user)
            return HttpResponseRedirect(user.get_profile_url())
    else:
        form = EditUserForm(user)
    return render_to_response('users/edit.html', {
                                                'form' : form,
                                                'gravatar_faq_url' : reverse('faq') + '#gravatar',
                                    }, context_instance=RequestContext(request))



def user_view(template, tab_name, tab_description, page_title):
    def decorator(fn):
        def decorated(request, id, slug=None):
            context = fn(request, get_object_or_404(User, id=id))
            context.update({
                "tab_name" : tab_name,
                "tab_description" : tab_description,
                "page_title" : page_title,
            })
            return render_to_response(template, context, context_instance=RequestContext(request))
        return decorated
    return decorator


@user_view('users/stats.html', 'stats', _('user profile'), _('user profile overview'))
def user_stats(request, user):
    questions = Question.objects.filter(author=user, deleted=False).order_by('-added_at')
    answers = Answer.objects.filter(author=user, deleted=False).order_by('-added_at')

    up_votes = user.get_up_vote_count()
    down_votes = user.get_down_vote_count()
    votes_today = user.get_vote_count_today()
    votes_total = int(settings.MAX_VOTES_PER_DAY)

    user_tags = Tag.objects.filter(Q(nodes__author=user) | Q(nodes__children__author=user)) \
        .annotate(user_tag_usage_count=Count('name')).order_by('-user_tag_usage_count')

    awards = Badge.objects.filter(award_badge__user=user).annotate(count=Count('name')).order_by('-count')

    if request.user.is_superuser:
        moderate_user_form = ModerateUserForm(instance=user)
    else:
        moderate_user_form = None

    return {'moderate_user_form': moderate_user_form,
            "view_user" : user,
            "questions" : questions,
            "answers" : answers,
            "up_votes" : up_votes,
            "down_votes" : down_votes,
            "total_votes": up_votes + down_votes,
            "votes_today_left": votes_total-votes_today,
            "votes_total_per_day": votes_total,
            "user_tags" : user_tags[:50],
            "awards": awards,
            "total_awards" : awards.count(),
        }

@user_view('users/recent.html', 'recent', _('recent user activity'), _('profile - recent activity'))
def user_recent(request, user):
    activities = Activity.objects.filter(activity_type__in=(TYPE_ACTIVITY_PRIZE,
            TYPE_ACTIVITY_ASK_QUESTION, TYPE_ACTIVITY_ANSWER,
            TYPE_ACTIVITY_COMMENT_QUESTION, TYPE_ACTIVITY_COMMENT_ANSWER,
            TYPE_ACTIVITY_MARK_ANSWER), user=user).order_by('-active_at')[:USERS_PAGE_SIZE]

    return {"view_user" : user, "activities" : activities}


@user_view('users/votes.html', 'votes', _('user vote record'), _('profile - votes'))
def user_votes(request, user):
    votes = user.votes.exclude(node__deleted=True).order_by('-voted_at')[:USERS_PAGE_SIZE]

    return {"view_user" : user, "votes" : votes}


@user_view('users/reputation.html', 'reputation', _('user reputation in the community'), _('profile - user reputation'))
def user_reputation(request, user):
    reputation = user.reputes.order_by('-reputed_at')

    graph_data = simplejson.dumps([
            (time.mktime(rep.reputed_at.timetuple()) * 1000, rep.reputation)
            for rep in reputation
    ])

    return {"view_user": user, "reputation": reputation, "graph_data": graph_data}

@user_view('users/questions.html', 'favorites', _('favorite questions'),  _('profile - favorite questions'))
def user_favorites(request, user):
    questions = user.favorite_questions.filter(deleted=False)

    return {"questions" : questions, "view_user" : user}

@user_view('users/subscriptions.html', 'subscriptions', _('subscription settings'), _('profile - subscriptions'))
def user_subscriptions(request, user):
    if request.method == 'POST':
        form = SubscriptionSettingsForm(request.POST)

        if 'notswitch' in request.POST:
            user.subscription_settings.enable_notifications = not user.subscription_settings.enable_notifications
            user.subscription_settings.save()

            if user.subscription_settings.enable_notifications:
                request.user.message_set.create(message=_('Notifications are now enabled'))
            else:
                request.user.message_set.create(message=_('Notifications are now disabled'))
        else:
            form.is_valid()
            for k,v in form.cleaned_data.items():
                setattr(user.subscription_settings, k, v)

            user.subscription_settings.save()
            request.user.message_set.create(message=_('New subscription settings are now saved'))
    else:
        form = SubscriptionSettingsForm(user.subscription_settings.__dict__)

    notificatons_on = user.subscription_settings.enable_notifications

    return {'view_user':user, 'notificatons_on': notificatons_on, 'form':form}

@login_required
def account_settings(request):
    logging.debug('')
    msg = request.GET.get('msg', '')
    is_openid = False

    return render_to_response('account_settings.html', {
        'msg': msg,
        'is_openid': is_openid
        }, context_instance=RequestContext(request))

