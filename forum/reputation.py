from django.db.models.signals import post_save
from forum.models.meta import vote_canceled

from forum.models import *
from forum.const import *
import settings

def on_flagged_item(instance, created, **kwargs):
    if not created:
        return

    post = instance.content_object
    question = (post.__class__ == Question) and post or post.question

    user.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED), question=question,
               reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED)


    if post.offensive_flag_count == settings.FLAG_COUNT_TO_HIDE_POST:
        post.author.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED_3_TIMES),
                   question=question, reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED_3_TIMES)

    if post.offensive_flag_count == settings.FLAG_COUNT_TO_DELETE_POST:
        post.author.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED_5_TIMES),
                   question=question, reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED_5_TIMES)

        post.mark_deleted(User.objects.get_site_owner())

post_save.connect(on_flagged_item, sender=FlaggedItem)


def on_answer_accepted_switch(instance, created, **kwargs):
    if not created and 'accepted' in instance.get_dirty_fields() and (
            not instance.accepted_by == instance.question.author):
        repute_type, repute_value = instance.accepted and (
            TYPE_REPUTATION_GAIN_BY_ANSWER_ACCEPTED, int(settings.REP_GAIN_BY_ACCEPTED)) or (
            TYPE_REPUTATION_LOST_BY_ACCEPTED_ANSWER_CANCELED, -int(settings.REP_LOST_BY_ACCEPTED_CANCELED))

        instance.author.reputes.create(value=repute_value, question=instance.question, reputation_type=repute_type)
        
        if instance.accepted_by == instance.question.author:
            repute_type, repute_value = instance.accepted and (
            TYPE_REPUTATION_GAIN_BY_ACCEPTING_ANSWER, int(settings.REP_GAIN_BY_ACCEPTING)) or (
            TYPE_REPUTATION_LOST_BY_CANCELLING_ACCEPTED_ANSWER, -int(settings.REP_LOST_BY_CANCELING_ACCEPTED))

            instance.question.author.reputes.create(value=repute_value, question=instance.question, reputation_type=repute_type)

post_save.connect(on_answer_accepted_switch, sender=Answer)


def on_vote(instance, created, **kwargs):
    if created and not instance.content_object.wiki:
        post = instance.content_object
        question = (post.__class__ == Question) and post or post.question

        if instance.vote == -1:
            instance.user.reputes.create(value=-int(settings.REP_LOST_BY_DOWNVOTING),
            question=question, reputation_type=TYPE_REPUTATION_LOST_BY_DOWNVOTING)

        if instance.vote == 1 and post.author.get_reputation_by_upvoted_today() >= int(settings.MAX_REP_BY_UPVOTE_DAY):
            return

        repute_type, repute_value = (instance.vote == 1) and (
            TYPE_REPUTATION_GAIN_BY_UPVOTED, int(settings.REP_GAIN_BY_UPVOTED)) or (
            TYPE_REPUTATION_LOST_BY_DOWNVOTED, -int(settings.REP_LOST_BY_DOWNVOTED))

        post.author.reputes.create(value=repute_value, question=question, reputation_type=repute_type)

post_save.connect(on_vote, sender=Vote)


def on_vote_canceled(instance, **kwargs):
    if not instance.content_object.wiki:
        post = instance.content_object
        question = (post.__class__ == Question) and post or post.question

        if instance.vote == -1:
            instance.user.reputes.create(value=int(settings.REP_GAIN_BY_CANCELING_DOWNVOTE),
            question=question, reputation_type=TYPE_REPUTATION_GAIN_BY_CANCELING_DOWNVOTE)

        repute_type, repute_value = (instance.vote == 1) and (
            TYPE_REPUTATION_LOST_BY_UPVOTE_CANCELED, -int(settings.REP_LOST_BY_UPVOTE_CANCELED)) or (
            TYPE_REPUTATION_GAIN_BY_DOWNVOTE_CANCELED, int(settings.REP_GAIN_BY_DOWNVOTE_CANCELED))

        post.author.reputes.create(value=repute_value, question=question, reputation_type=repute_type)

vote_canceled.connect(on_vote_canceled)


    


