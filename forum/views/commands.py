import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ungettext, ugettext as _
from django.template import RequestContext
from forum.models import *
from forum.forms import CloseForm
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from forum.utils.decorators import ajax_method, ajax_login_required
from decorators import command
import logging

class NotEnoughRepPointsException(Exception):
    def __init__(self, action):
        super(NotEnoughRepPointsException, self).__init__(
            _("""
            Sorry, but you don't have enough reputation points to %(action)s.<br />
            Please check the <a href'%(faq_url)s'>faq</a>
            """ % {'action': action, 'faq_url': reverse('faq')})
        )

class CannotDoOnOwnException(Exception):
    def __init__(self, action):
        super(CannotDoOnOwnException, self).__init__(
            _("""
            Sorry but you cannot %(action)s your own post.<br />
            Please check the <a href'%(faq_url)s'>faq</a>
            """ % {'action': action, 'faq_url': reverse('faq')})
        )

class AnonymousNotAllowedException(Exception):
    def __init__(self, action):
        super(AnonymousNotAllowedException, self).__init__(
            _("""
            Sorry but anonymous users cannot %(action)s.<br />
            Please login or create an account <a href'%(signin_url)s'>here</a>.
            """ % {'action': action, 'signin_url': reverse('auth_signin')})
        )

class NotEnoughLeftException(Exception):
    def __init__(self, action, limit):
        super(NotEnoughRepPointsException, self).__init__(
            _("""
            Sorry, but you don't have enough %(action)s left for today..<br />
            The limit is %(limit)s per day..<br />
            Please check the <a href'%(faq_url)s'>faq</a>
            """ % {'action': action, 'limit': limit, 'faq_url': reverse('faq')})
        )

class CannotDoubleActionException(Exception):
    def __init__(self, action):
        super(CannotDoubleActionException, self).__init__(
            _("""
            Sorry, but you cannot %(action)s twice the same post.<br />
            Please check the <a href'%(faq_url)s'>faq</a>
            """ % {'action': action, 'faq_url': reverse('faq')})
        )


@command
def vote_post(request, id, vote_type):
    post = get_object_or_404(Node, id=id)
    vote_score = vote_type == 'up' and 1 or -1
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('vote'))

    if user == post.author:
        raise CannotDoOnOwnException(_('vote'))

    if not (vote_type == 'up' and user.can_vote_up() or user.can_vote_down()):
        raise NotEnoughRepPointsException(vote_type == 'up' and _('upvote') or _('downvote'))

    user_vote_count_today = user.get_vote_count_today()

    if user_vote_count_today >= int(settings.MAX_VOTES_PER_DAY):
        raise NotEnoughLeftException(_('votes'), str(settings.MAX_VOTES_PER_DAY))

    try:
        vote = post.votes.get(canceled=False, user=user)

        if vote.voted_at < datetime.datetime.now() - datetime.timedelta(days=int(settings.DENY_UNVOTE_DAYS)):
            raise Exception(
                    _("Sorry but you cannot cancel a vote after %(ndays)d %(tdays)s from the original vote") %
                    {'ndays': int(settings.DENY_UNVOTE_DAYS), 'tdays': ungettext('day', 'days', int(settings.DENY_UNVOTE_DAYS))}
            )

        vote.cancel()
        vote_type = 'none'
    except ObjectDoesNotExist:
        #there is no vote yet
        vote = Vote(user=user, node=post, vote=vote_score)
        vote.save()

    response = {
        'commands': {
            'update_post_score': [id, vote.vote * (vote_type == 'none' and -1 or 1)],
            'update_user_post_vote': [id, vote_type]
        }
    }

    votes_left = int(settings.MAX_VOTES_PER_DAY) - user_vote_count_today + (vote_type == 'none' and -1 or 1)

    if int(settings.START_WARN_VOTES_LEFT) >= votes_left:
        response['message'] = _("You have %(nvotes)s %(tvotes)s left today.") % \
                    {'nvotes': votes_left, 'tvotes': ungettext('vote', 'votes', votes_left)}

    return response

@command
def flag_post(request, id):
    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('flag posts'))

    if user == post.author:
        raise CannotDoOnOwnException(_('flag'))

    if not (user.can_flag_offensive(post)):
        raise NotEnoughRepPointsException(_('flag posts'))

    user_flag_count_today = user.get_flagged_items_count_today()

    if user_flag_count_today >= int(settings.MAX_FLAGS_PER_DAY):
        raise NotEnoughLeftException(_('flags'), str(settings.MAX_FLAGS_PER_DAY))

    try:
        post.flaggeditems.get(user=user)
        raise CannotDoubleActionException(_('flag'))
    except ObjectDoesNotExist:
        flag = FlaggedItem(user=user, content_object=post)
        flag.save()

    return {}
        
@command
def like_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('like comments'))

    if user == comment.user:
        raise CannotDoOnOwnException(_('like'))

    if not user.can_like_comment(comment):
        raise NotEnoughRepPointsException( _('like comments'))    

    try:
        like = LikedComment.active.get(comment=comment, user=user)
        like.cancel()
        likes = False
    except ObjectDoesNotExist:
        like = LikedComment(comment=comment, user=user)
        like.save()
        likes = True

    return {
        'commands': {
            'update_comment_score': [comment.id, likes and 1 or -1],
            'update_likes_comment_mark': [comment.id, likes and 'on' or 'off']
        }
    }

@command
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('delete comments'))

    if not user.can_delete_comment(comment):
        raise NotEnoughRepPointsException( _('delete comments'))

    comment.mark_deleted(user)

    return {
        'commands': {
            'remove_comment': [comment.id],
        }
    }

@command
def mark_favorite(request, id):
    question = get_object_or_404(Question, id=id)

    if not request.user.is_authenticated():
        raise AnonymousNotAllowedException(_('mark a question as favorite'))

    try:
        favorite = FavoriteQuestion.objects.get(question=question, user=request.user)
        favorite.delete()
        added = False
    except ObjectDoesNotExist:
        favorite = FavoriteQuestion(question=question, user=request.user)
        favorite.save()
        added = True

    return {
        'commands': {
            'update_favorite_count': [added and 1 or -1],
            'update_favorite_mark': [added and 'on' or 'off']
        }
    }

@command
def comment(request, id):
    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('comment'))

    if not request.method == 'POST':
        raise Exception(_("Invalid request"))

    if 'id' in request.POST:
        comment = get_object_or_404(Comment, id=request.POST['id'])

        if not user.can_edit_comment(comment):
            raise NotEnoughRepPointsException( _('edit comments'))
    else:
        if not user.can_comment(post):
            raise NotEnoughRepPointsException( _('comment'))

        comment = Comment(parent=post)

    comment_text = request.POST.get('comment', '').strip()

    if not len(comment_text):
        raise Exception(_("Comment is empty"))

    comment.create_revision(user, body=comment_text)

    if comment.active_revision.revision == 1:
        return {
            'commands': {
                'insert_comment': [
                    id, comment.id, comment_text, user.username, user.get_profile_url(), reverse('delete_comment', kwargs={'id': comment.id})
                ]
            }
        }
    else:
        return {
            'commands': {
                'update_comment': [comment.id, comment.comment]
            }
        }


@command
def accept_answer(request, id):
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('accept answers'))

    answer = get_object_or_404(Answer, id=id)
    question = answer.question

    if not user.can_accept_answer(answer):
        raise Exception(_("Sorry but only the question author can accept an answer"))

    commands = {}

    if answer.accepted:
        answer.unmark_accepted(user)
        commands['unmark_accepted'] = [answer.id]
    else:
        if question.accepted_answer is not None:
            accepted = question.accepted_answer
            accepted.unmark_accepted(user)
            commands['unmark_accepted'] = [accepted.id]

        answer.mark_accepted(user)
        commands['mark_accepted'] = [answer.id]

    return {'commands': commands}

@command    
def delete_post(request, id):
    post = get_object_or_404(Node, id=id)
    user = request.user

    if not user.is_authenticated():
        raise AnonymousNotAllowedException(_('delete posts'))

    if not (user.can_delete_post(post)):
        raise NotEnoughRepPointsException(_('delete posts'))

    post.mark_deleted(user)

    return {
        'commands': {
                'mark_deleted': [post.node_type, id]
            }
    }

@command
def subscribe(request, id):
    question = get_object_or_404(Question, id=id)

    try:
        subscription = QuestionSubscription.objects.get(question=question, user=request.user)
        subscription.delete()
        subscribed = False
    except:
        subscription = QuestionSubscription(question=question, user=request.user, auto_subscription=False)
        subscription.save()
        subscribed = True

    return {
        'commands': {
                'set_subscription_button': [subscribed and _('unsubscribe me') or _('subscribe me')],
                'set_subscription_status': ['']
            }
    }

#internally grouped views - used by the tagging system
@ajax_login_required
def mark_tag(request, tag=None, **kwargs):#tagging system
    action = kwargs['action']
    ts = MarkedTag.objects.filter(user=request.user, tag__name=tag)
    if action == 'remove':
        logging.debug('deleting tag %s' % tag)
        ts.delete()
    else:
        reason = kwargs['reason']
        if len(ts) == 0:
            try:
                t = Tag.objects.get(name=tag)
                mt = MarkedTag(user=request.user, reason=reason, tag=t)
                mt.save()
            except:
                pass
        else:
            ts.update(reason=reason)
    return HttpResponse(simplejson.dumps(''), mimetype="application/json")

@ajax_login_required
def ajax_toggle_ignored_questions(request):#ajax tagging and tag-filtering system
    if request.user.hide_ignored_questions:
        new_hide_setting = False
    else:
        new_hide_setting = True
    request.user.hide_ignored_questions = new_hide_setting
    request.user.save()

@ajax_method
def ajax_command(request):#refactor? view processing ajax commands - note "vote" and view others do it too
    if 'command' not in request.POST:
        return HttpResponseForbidden(mimetype="application/json")
    if request.POST['command'] == 'toggle-ignored-questions':
        return ajax_toggle_ignored_questions(request)

@login_required
def close(request, id):#close question
    """view to initiate and process 
    question close
    """
    question = get_object_or_404(Question, id=id)
    if not request.user.can_close_question(question):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = CloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            question.closed = True
            question.closed_by = request.user
            question.closed_at = datetime.datetime.now()
            question.close_reason = reason
            question.save()
        return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = CloseForm()
        return render_to_response('close.html', {
            'form' : form,
            'question' : question,
            }, context_instance=RequestContext(request))

@login_required
def reopen(request, id):#re-open question
    """view to initiate and process 
    question close
    """
    question = get_object_or_404(Question, id=id)
    # open question
    if not request.user.can_reopen_question(question):
        return HttpResponseForbidden()
    if request.method == 'POST' :
        Question.objects.filter(id=question.id).update(closed=False,
            closed_by=None, closed_at=None, close_reason=None)
        return HttpResponseRedirect(question.get_absolute_url())
    else:
        return render_to_response('reopen.html', {
            'question' : question,
            }, context_instance=RequestContext(request))

#osqa-user communication system
def read_message(request):#marks message a read
    if request.method == "POST":
        if request.POST['formdata'] == 'required':
            request.session['message_silent'] = 1
            if request.user.is_authenticated():
                request.user.delete_messages()
    return HttpResponse('')


