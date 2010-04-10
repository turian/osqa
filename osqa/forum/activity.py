import datetime
from django.db.models.signals import post_save
from forum.models import *
from forum.models.base import marked_deleted
from forum.models.meta import vote_canceled
from forum.authentication import user_updated
from forum.const import *

def record_ask_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=TYPE_ACTIVITY_ASK_QUESTION)
        activity.save()

post_save.connect(record_ask_event, sender=Question)


def record_answer_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.author, active_at=instance.added_at, content_object=instance, activity_type=TYPE_ACTIVITY_ANSWER)
        activity.save()

post_save.connect(record_answer_event, sender=Answer)


def record_comment_event(instance, created, **kwargs):
    if created:
        act_type = (instance.content_object.__class__ is Question) and TYPE_ACTIVITY_COMMENT_QUESTION or TYPE_ACTIVITY_COMMENT_ANSWER
        activity = Activity(user=instance.user, active_at=instance.added_at, content_object=instance, activity_type=act_type)
        activity.save()

post_save.connect(record_comment_event, sender=Comment)


def record_question_revision_event(instance, created, **kwargs):
    if created and instance.revision <> 1:
        activity = Activity(user=instance.author, active_at=instance.revised_at, content_object=instance, activity_type=TYPE_ACTIVITY_UPDATE_QUESTION)
        activity.save()

post_save.connect(record_question_revision_event, sender=QuestionRevision)


def record_answer_revision_event(instance, created, **kwargs):
    if created and instance.revision <> 1:
        activity = Activity(user=instance.author, active_at=instance.revised_at, content_object=instance, activity_type=TYPE_ACTIVITY_UPDATE_ANSWER)
        activity.save()

post_save.connect(record_answer_revision_event, sender=AnswerRevision)


def record_award_event(instance, created, **kwargs):
    if created:
        activity = Activity(user=instance.user, active_at=instance.awarded_at, content_object=instance,
            activity_type=TYPE_ACTIVITY_PRIZE)
        activity.save()

post_save.connect(record_award_event, sender=Award)


def record_answer_accepted(instance, created, **kwargs):
    if not created and 'accepted' in instance.get_dirty_fields() and instance.accepted:
        activity = Activity(user=instance.question.author, active_at=datetime.datetime.now(), \
            content_object=instance, activity_type=TYPE_ACTIVITY_MARK_ANSWER)
        activity.save()

post_save.connect(record_answer_accepted, sender=Answer)


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

vote_canceled.connect(record_cancel_vote)


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

