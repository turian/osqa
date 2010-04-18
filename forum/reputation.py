from django.db.models.signals import post_save
from forum.models.base import mark_canceled
from forum.models.answer import answer_accepted, answer_accepted_canceled

from forum.models import *
from forum.const import *
import settings

def on_flagged_item(instance, created, **kwargs):
    if not created:
        return

    post = instance.content_object.leaf
    question = (post.__class__ == Question) and post or post.question

    post.author.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED), question=question,
               reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED)


    if post.offensive_flag_count == settings.FLAG_COUNT_TO_HIDE_POST:
        post.author.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED_3_TIMES),
                   question=question, reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED_3_TIMES)

    if post.offensive_flag_count == settings.FLAG_COUNT_TO_DELETE_POST:
        post.author.reputes.create(value=-int(settings.REP_LOST_BY_FLAGGED_5_TIMES),
                   question=question, reputation_type=TYPE_REPUTATION_LOST_BY_FLAGGED_5_TIMES)

        post.mark_deleted(User.objects.get_site_owner())

post_save.connect(on_flagged_item, sender=FlaggedItem)

def on_answer_accepted(answer, user, **kwargs):
    if user == answer.question.author and not user == answer.author:
        user.reputes.create(
            value=int(settings.REP_GAIN_BY_ACCEPTING), question=answer.question,
            reputation_type=TYPE_REPUTATION_GAIN_BY_ACCEPTING_ANSWER)

    if not user == answer.author:
        answer.author.reputes.create(
            value=int(settings.REP_GAIN_BY_ACCEPTED), question=answer.question,
            reputation_type=TYPE_REPUTATION_GAIN_BY_ANSWER_ACCEPTED)

answer_accepted.connect(on_answer_accepted)


def on_answer_accepted_canceled(answer, user, **kwargs):
    if user == answer.accepted_by:
        user.reputes.create(
            value=-int(settings.REP_LOST_BY_CANCELING_ACCEPTED), question=answer.question,
            reputation_type=TYPE_REPUTATION_LOST_BY_CANCELLING_ACCEPTED_ANSWER)

    if not user == answer.author:
        answer.author.reputes.create(
            value=-int(settings.REP_LOST_BY_ACCEPTED_CANCELED), question=answer.question,
            reputation_type=TYPE_REPUTATION_LOST_BY_ACCEPTED_ANSWER_CANCELED)

answer_accepted_canceled.connect(on_answer_accepted)


def on_vote(instance, created, **kwargs):
    if created and (instance.content_object.node_type in ("question", "answer") and not instance.content_object.wiki):
        post = instance.content_object.leaf
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
    if instance.content_object.node_type in ("question", "answer") and not instance.content_object.wiki:
        post = instance.content_object.leaf
        question = (post.__class__ == Question) and post or post.question

        if instance.vote == -1:
            instance.user.reputes.create(value=int(settings.REP_GAIN_BY_CANCELING_DOWNVOTE),
            question=question, reputation_type=TYPE_REPUTATION_GAIN_BY_CANCELING_DOWNVOTE)

        repute_type, repute_value = (instance.vote == 1) and (
            TYPE_REPUTATION_LOST_BY_UPVOTE_CANCELED, -int(settings.REP_LOST_BY_UPVOTE_CANCELED)) or (
            TYPE_REPUTATION_GAIN_BY_DOWNVOTE_CANCELED, int(settings.REP_GAIN_BY_DOWNVOTE_CANCELED))

        post.author.reputes.create(value=repute_value, question=question, reputation_type=repute_type)

mark_canceled.connect(on_vote_canceled, sender=Vote)


    


