import datetime
from django.db.models.signals import post_save
from forum.models import *
from forum.models.base import marked_deleted, mark_canceled
from forum.models.node import node_create
from forum.models.answer import answer_accepted
from forum.authentication import user_updated
from forum.const import *

def record_ask_event(instance, **kwargs):
    activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=TYPE_ACTIVITY_ASK_QUESTION)
    activity.save()

node_create.connect(record_ask_event, sender=Question)


def record_answer_event(instance, **kwargs):
    activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=TYPE_ACTIVITY_ANSWER)
    activity.save()

node_create.connect(record_answer_event, sender=Answer)


def record_comment_event(instance, **kwargs):
    act_type = (instance.content_object.__class__ is Question) and TYPE_ACTIVITY_COMMENT_QUESTION or TYPE_ACTIVITY_COMMENT_ANSWER
    activity = Activity(user=instance.user, active_at=instance.added_at, content_object=instance, activity_type=act_type)
    activity.save()

node_create.connect(record_comment_event, sender=Comment)


def record_revision_event(instance, created, **kwargs):
    if created and instance.revision <> 1 and instance.node.node_type in ('question', 'answer',):
        activity_type = instance.node.node_type == 'question' and TYPE_ACTIVITY_UPDATE_QUESTION or TYPE_ACTIVITY_UPDATE_ANSWER
        activity = Activity(user=instance.author, active_at=instance.revised_at, content_object=instance, activity_type=activity_type)
        activity.save()

post_save.connect(record_revision_event, sender=NodeRevision)


def record_award_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.user, active_at=instance.awarded_at, content_object=instance,
            activity_type=TYPE_ACTIVITY_PRIZE)
        activity.save()

post_save.connect(record_award_event, sender=Award)


def record_answer_accepted(answer, user, **kwargs):
    activity = Activity(user=user, active_at=datetime.datetime.now(), content_object=answer, activity_type=TYPE_ACTIVITY_MARK_ANSWER)
    activity.save()

answer_accepted.connect(record_answer_accepted)


def update_last_seen(instance, **kwargs):
    user = instance.user
    user.last_seen = datetime.datetime.now()
    user.save()

post_save.connect(update_last_seen, sender=Activity)


def record_vote(instance, created, **kwargs):
    if created:
        act_type = (instance.vote == 1) and TYPE_ACTIVITY_VOTE_UP or TYPE_ACTIVITY_VOTE_DOWN

        activity = Activity(user=instance.user, active_at=instance.voted_at, content_object=instance, activity_type=act_type)
        activity.save()

post_save.connect(record_vote, sender=Vote)


def record_cancel_vote(instance, **kwargs):
    act_type = (instance.vote == 1) and TYPE_ACTIVITY_CANCEL_VOTE_UP or TYPE_ACTIVITY_CANCEL_VOTE_DOWN
    activity = Activity(user=instance.user, active_at=datetime.datetime.now(), content_object=instance, activity_type=act_type)
    activity.save()

mark_canceled.connect(record_cancel_vote, sender=Vote)


def record_delete_post(instance, **kwargs):
    act_type = (instance.__class__ is Question) and TYPE_ACTIVITY_DELETE_QUESTION or TYPE_ACTIVITY_DELETE_ANSWER
    activity = Activity(user=instance.deleted_by, active_at=datetime.datetime.now(), content_object=instance, activity_type=act_type)
    activity.save()

marked_deleted.connect(record_delete_post, sender=Question)
marked_deleted.connect(record_delete_post, sender=Answer)


def record_update_tags(instance, created, **kwargs):
    if not created and 'tagnames' in instance.get_dirty_fields():
        activity = Activity(user=instance.author, active_at=datetime.datetime.now(), content_object=instance, activity_type=TYPE_ACTIVITY_UPDATE_TAGS)
        activity.save()

post_save.connect(record_update_tags, sender=Question)


def record_mark_offensive(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.user, active_at=datetime.datetime.now(), content_object=instance.content_object, activity_type=TYPE_ACTIVITY_MARK_OFFENSIVE)
        activity.save()

post_save.connect(record_mark_offensive, sender=FlaggedItem)


def record_favorite_question(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.user, active_at=datetime.datetime.now(), content_object=instance, activity_type=TYPE_ACTIVITY_FAVORITE)
        activity.save()

post_save.connect(record_favorite_question, sender=FavoriteQuestion)


def record_user_full_updated(instance, **kwargs):
    activity = Activity(user=instance, active_at=datetime.datetime.now(), content_object=instance, activity_type=TYPE_ACTIVITY_USER_FULL_UPDATED)
    activity.save()

user_updated.connect(record_user_full_updated, sender=User)

