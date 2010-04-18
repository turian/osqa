from datetime import datetime, timedelta

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.db.models import Sum

from forum.settings.base import Setting
from forum.settings.forms import SettingsSetForm

from forum.models import Activity, Question, Answer, User, Node
from forum import const
from forum import settings

def super_user_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            return fn(request, *args, **kwargs)
        else:
            raise Http404

    return wrapper

@super_user_required
def index(request):
    return render_to_response('osqaadmin/index.html', {
        'sets': get_all_sets(),
        'settings_pack': settings.SETTINGS_PACK,
        'statistics': get_statistics(),
        'recent_activity': get_recent_activity(),
    }, context_instance=RequestContext(request))

@super_user_required    
def settings_set(request, set_name):
    set = Setting.sets.get(set_name, None)

    if set is None:
        raise Http404

    if request.POST:
        form = SettingsSetForm(set, data=request.POST, files=request.FILES)

        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_("'%s' settings saved succesfully") % set_name)

            if set_name in ('minrep', 'badges', 'repgain'):
                settings.SETTINGS_PACK.set_value("custom")
    else:
        form = SettingsSetForm(set)

    return render_to_response('osqaadmin/set.html', {
        'form': form,
        'sets': get_all_sets(),
    }, context_instance=RequestContext(request))

def get_all_sets():
    return sorted(Setting.sets.values(), lambda s1, s2: s1.weight - s2.weight)

def get_recent_activity():
    return Activity.objects.filter(activity_type__in=(
            const.TYPE_ACTIVITY_ASK_QUESTION, const.TYPE_ACTIVITY_ANSWER,
            const.TYPE_ACTIVITY_COMMENT_QUESTION, const.TYPE_ACTIVITY_COMMENT_ANSWER,
            const.TYPE_ACTIVITY_MARK_ANSWER)).order_by('-active_at')[0:10]

def get_statistics():
    return {
        'total_users': User.objects.all().count(),
        'users_last_24': User.objects.filter(date_joined__gt=(datetime.now() - timedelta(days=1))).count(),
        'total_questions': Question.objects.filter(deleted=False).count(),
        'questions_last_24': Question.objects.filter(deleted=False, added_at__gt=(datetime.now() - timedelta(days=1))).count(),
        'total_answers': Answer.objects.filter(deleted=False).count(),
        'answers_last_24': Answer.objects.filter(deleted=False, added_at__gt=(datetime.now() - timedelta(days=1))).count(),
    }

@super_user_required      
def go_bootstrap(request):
    #todo: this is the quick and dirty way of implementing a bootstrap mode
    try:
        from forum_modules.default_badges import settings as dbsets
        dbsets.POPULAR_QUESTION_VIEWS.set_value(100)
        dbsets.NOTABLE_QUESTION_VIEWS.set_value(200)
        dbsets.FAMOUS_QUESTION_VIEWS.set_value(300)
        dbsets.NICE_ANSWER_VOTES_UP.set_value(2)
        dbsets.NICE_QUESTION_VOTES_UP.set_value(2)
        dbsets.GOOD_ANSWER_VOTES_UP.set_value(4)
        dbsets.GOOD_QUESTION_VOTES_UP.set_value(4)
        dbsets.GREAT_ANSWER_VOTES_UP.set_value(8)
        dbsets.GREAT_QUESTION_VOTES_UP.set_value(8)
        dbsets.FAVORITE_QUESTION_FAVS.set_value(1)
        dbsets.STELLAR_QUESTION_FAVS.set_value(3)
        dbsets.DISCIPLINED_MIN_SCORE.set_value(3)
        dbsets.PEER_PRESSURE_MAX_SCORE.set_value(-3)
        dbsets.CIVIC_DUTY_VOTES.set_value(15)
        dbsets.PUNDIT_COMMENT_COUNT.set_value(10)
        dbsets.SELF_LEARNER_UP_VOTES.set_value(2)
        dbsets.STRUNK_AND_WHITE_EDITS.set_value(10)
        dbsets.ENLIGHTENED_UP_VOTES.set_value(2)
        dbsets.GURU_UP_VOTES.set_value(4)
        dbsets.NECROMANCER_UP_VOTES.set_value(2)
        dbsets.NECROMANCER_DIF_DAYS.set_value(30)
        dbsets.TAXONOMIST_USE_COUNT.set_value(5)
    except:
        pass

    settings.REP_TO_VOTE_UP.set_value(0)
    settings.REP_TO_VOTE_DOWN.set_value(15)
    settings.REP_TO_FLAG.set_value(15)
    settings.REP_TO_COMMENT.set_value(0)
    settings.REP_TO_LIKE_COMMENT.set_value(0)
    settings.REP_TO_UPLOAD.set_value(0)
    settings.REP_TO_CLOSE_OWN.set_value(60)
    settings.REP_TO_REOPEN_OWN.set_value(120)
    settings.REP_TO_RETAG.set_value(150)
    settings.REP_TO_EDIT_WIKI.set_value(200)
    settings.REP_TO_EDIT_OTHERS.set_value(400)
    settings.REP_TO_CLOSE_OTHERS.set_value(600)
    settings.REP_TO_DELETE_COMMENTS.set_value(400)
    settings.REP_TO_VIEW_FLAGS.set_value(30)

    settings.INITIAL_REP.set_value(1)
    settings.MAX_REP_BY_UPVOTE_DAY.set_value(300)
    settings.REP_GAIN_BY_UPVOTED.set_value(15)
    settings.REP_LOST_BY_UPVOTE_CANCELED.set_value(15)
    settings.REP_LOST_BY_DOWNVOTED.set_value(1)
    settings.REP_LOST_BY_DOWNVOTING.set_value(0)
    settings.REP_GAIN_BY_DOWNVOTE_CANCELED.set_value(1)
    settings.REP_GAIN_BY_CANCELING_DOWNVOTE.set_value(0)
    settings.REP_GAIN_BY_ACCEPTED.set_value(25)
    settings.REP_LOST_BY_ACCEPTED_CANCELED.set_value(25)
    settings.REP_GAIN_BY_ACCEPTING.set_value(5)
    settings.REP_LOST_BY_CANCELING_ACCEPTED.set_value(5)
    settings.REP_LOST_BY_FLAGGED.set_value(2)
    settings.REP_LOST_BY_FLAGGED_3_TIMES.set_value(30)
    settings.REP_LOST_BY_FLAGGED_5_TIMES.set_value(100)

    settings.SETTINGS_PACK.set_value("bootstrap")

    request.user.message_set.create(message=_('Bootstrap mode enabled'))
    return HttpResponseRedirect(reverse('admin_index'))

@super_user_required
def go_defaults(request):
    for setting in Setting.sets['badges']:
        setting.to_default()
    for setting in Setting.sets['minrep']:
        setting.to_default()
    for setting in Setting.sets['repgain']:
        setting.to_default()

    settings.SETTINGS_PACK.set_value("default")

    request.user.message_set.create(message=_('All values reverted to defaults'))
    return HttpResponseRedirect(reverse('admin_index'))


@super_user_required
def recalculate_denormalized(request):
    for n in Node.objects.all():
        n.vote_up_count = n.votes.filter(canceled=False, vote=1).count()
        n.vote_down_count = n.votes.filter(canceled=False, vote=-1).count()
        n.save()

    for u in User.objects.all():
        u.reputation = u.reputes.filter(canceled=False).aggregate(reputation=Sum('value'))['reputation']
        u.save()

    request.user.message_set.create(message=_('All values recalculated'))
    return HttpResponseRedirect(reverse('admin_index'))

