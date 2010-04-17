from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from forum.forms import FeedbackForm
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _
from forum.utils.forms import get_next_url
from forum.models import Badge, Award, User
from forum.badges import ALL_BADGES
from forum import settings
from forum.utils.mail import send_email
import re

def favicon(request):
    return HttpResponseRedirect(str(settings.APP_FAVICON))

def about(request):
    return render_to_response('about.html', {'text': settings.ABOUT_PAGE_TEXT.value }, context_instance=RequestContext(request))

def faq(request):
    data = {
        'gravatar_faq_url': reverse('faq') + '#gravatar',
        #'send_email_key_url': reverse('send_email_key'),
        'ask_question_url': reverse('ask'),
    }
    return render_to_response('faq.html', data, context_instance=RequestContext(request))

def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            context = {'user': request.user}

            if not request.user.is_authenticated:
                context['email'] = form.cleaned_data.get('email',None)
            context['message'] = form.cleaned_data['message']
            context['name'] = form.cleaned_data.get('name',None)

            recipients = [(adm.username, adm.email) for adm in User.objects.filter(is_superuser=True)]

            send_email(settings.EMAIL_SUBJECT_PREFIX + _("Feedback message from %(site_name)s") % {'site_name': settings.APP_SHORT_NAME},
                       recipients, "notifications/feedback.html", context)
            
            msg = _('Thanks for the feedback!')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect(get_next_url(request))
    else:
        form = FeedbackForm(initial={'next':get_next_url(request)})

    return render_to_response('feedback.html', {'form': form}, context_instance=RequestContext(request))
feedback.CANCEL_MESSAGE=_('We look forward to hearing your feedback! Please, give it next time :)')

def privacy(request):
    return render_to_response('privacy.html', context_instance=RequestContext(request))

def logout(request):
    return render_to_response('logout.html', {
        'next' : get_next_url(request),
    }, context_instance=RequestContext(request))

def badges(request):#user status/reputation system
    badges = Badge.objects.all().order_by('name')

    badges_dict = dict([(badge.badge, badge.description) for badge in ALL_BADGES])

    for badge in badges:
        if badge.description != badges_dict.get(badge.slug, badge.description):
            badge.description = badges_dict[badge.slug]
            badge.save()
    
    my_badges = []
    if request.user.is_authenticated():
        my_badges = Award.objects.filter(user=request.user).values('badge_id')
        #my_badges.query.group_by = ['badge_id']

    return render_to_response('badges.html', {
        'badges' : badges,
        'mybadges' : my_badges,
        'feedback_faq_url' : reverse('feedback'),
    }, context_instance=RequestContext(request))

def badge(request, id):
    badge = get_object_or_404(Badge, id=id)
    awards = Award.objects.extra(
        select={'id': 'auth_user.id', 
                'name': 'auth_user.username', 
                'rep':'forum_user.reputation',
                'gold': 'forum_user.gold',
                'silver': 'forum_user.silver',
                'bronze': 'forum_user.bronze'},
        tables=['award', 'auth_user', 'forum_user'],
        where=['badge_id=%s AND user_id=auth_user.id AND forum_user.user_ptr_id = auth_user.id'],
        params=[id]
    ).distinct('id')

    return render_to_response('badge.html', {
        'awards' : awards,
        'badge' : badge,
    }, context_instance=RequestContext(request))

