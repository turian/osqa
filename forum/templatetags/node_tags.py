from datetime import datetime, timedelta

from forum.models import Question, FavoriteQuestion
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('node/vote_buttons.html')
def vote_buttons(post, user):
    context = {
        'post': post,
        'user_vote': 'none'
    }

    if user.is_authenticated():
        try:
            vote = post.votes.get(user=user)
            context['user_vote'] = vote.is_upvote() and 'up' or 'down'
        except:
            pass

    return context

@register.inclusion_tag('node/accept_button.html')
def accept_button(answer, user):
    return {
        'can_accept': user.is_authenticated() and user.can_accept_answer(answer),
        'answer': answer,
        'user': user
    }

@register.inclusion_tag('node/favorite_mark.html')
def favorite_mark(question, user):
    try:
        FavoriteQuestion.objects.get(question=question, user=user)
        favorited = True
    except:
        favorited = False

    favorite_count = question.favorited_by.count()

    return {'favorited': favorited, 'favorite_count': favorite_count, 'question': question}

def post_control(text, url, command=False, title=""):
    return {'text': text, 'url': url, 'command': command, 'title': title}

@register.inclusion_tag('node/post_controls.html')
def post_controls(post, user):
    controls = []

    if user.is_authenticated():
        post_type = (post.__class__ is Question) and 'question' or 'answer'

        if post_type == "answer":
            controls.append(post_control(_('permanent link'), '#%d' % post.id, title=_("answer permanent link")))

        edit_url = reverse('edit_' + post_type, kwargs={'id': post.id})
        if user.can_edit_post(post):
            controls.append(post_control(_('edit'), edit_url))
        elif post_type == 'question' and user.can_retag_questions():
            controls.append(post_control(_('retag'), edit_url))

        if post_type == 'question':
            if post.closed and user.can_reopen_question(post):
                controls.append(post_control(_('reopen'), reverse('reopen', kwargs={'id': post.id})))
            elif not post.closed and user.can_close_question(post):
                controls.append(post_control(_('close'), reverse('close', kwargs={'id': post.id})))

        if user.can_flag_offensive(post):
            label = _('flag')
            
            if user.can_view_offensive_flags(post):
                label =  "%s (%d)" % (label, post.flaggeditems.count())

            controls.append(post_control(label, reverse('flag_post', kwargs={'id': post.id}),
                    command=True, title=_("report as offensive (i.e containing spam, advertising, malicious text, etc.)")))

        if user.can_delete_post(post):
            controls.append(post_control(_('delete'), reverse('delete_post', kwargs={'id': post.id}),
                    command=True))

    return {'controls': controls}

@register.inclusion_tag('node/comments.html')
def comments(post, user):
    all_comments = post.comments.filter(deleted=False).order_by('added_at')

    if len(all_comments) <= 5:
        top_scorers = all_comments
    else:
        top_scorers = sorted(all_comments, lambda c1, c2: c2.score - c1.score)[0:5]

    comments = []
    showing = 0
    for c in all_comments:
        context = {
            'can_delete': user.can_delete_comment(c),
            'can_like': user.can_like_comment(c),
            'can_edit': user.can_edit_comment(c)
        }

        if c in top_scorers or c.is_reply_to(user):
            context['top_scorer'] = True
            showing += 1
        
        if context['can_like']:
            try:
                c.votes.get(user=user)
                context['likes'] = True
            except:
                context['likes'] = False

        context['user'] = c.user
        context.update(dict(c.__dict__))
        comments.append(context)

    return {
        'comments': comments,
        'post': post,
        'can_comment': user.can_comment(post),
        'max_length': settings.FORM_MAX_COMMENT_BODY,
        'showing': showing,
        'total': len(all_comments),
    }
