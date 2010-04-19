from datetime import timedelta

from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

from forum.badges.base import PostCountableAbstractBadge, ActivityAbstractBadge, FirstActivityAbstractBadge, \
        ActivityCountAbstractBadge, CountableAbstractBadge, AbstractBadge, NodeCountableAbstractBadge
from forum.models import Node, Question, Answer, Activity, Tag
from forum.models.user import activity_record
from forum.models.base import denorm_update
from forum import const

import settings

class PopularQuestionBadge(PostCountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Asked a question with %s views') % str(settings.POPULAR_QUESTION_VIEWS)

    def __init__(self):
        super(PopularQuestionBadge, self).__init__(Question, 'view_count', settings.POPULAR_QUESTION_VIEWS)

class NotableQuestionBadge(PostCountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Asked a question with %s views') % str(settings.NOTABLE_QUESTION_VIEWS)

    def __init__(self):
        super(NotableQuestionBadge, self).__init__(Question, 'view_count', settings.NOTABLE_QUESTION_VIEWS)

class FamousQuestionBadge(PostCountableAbstractBadge):
    type = const.GOLD_BADGE
    description = _('Asked a question with %s views') % str(settings.FAMOUS_QUESTION_VIEWS)

    def __init__(self):
        super(FamousQuestionBadge, self).__init__(Question, 'view_count', settings.FAMOUS_QUESTION_VIEWS)


class NiceAnswerBadge(NodeCountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Answer voted up %s times') % str(settings.NICE_ANSWER_VOTES_UP)

    def __init__(self):
        super(NiceAnswerBadge, self).__init__("answer", 'vote_up_count', settings.NICE_ANSWER_VOTES_UP)

class NiceQuestionBadge(NodeCountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Question voted up %s times') % str(settings.NICE_QUESTION_VOTES_UP)

    def __init__(self):
        super(NiceQuestionBadge, self).__init__("question", 'vote_up_count', settings.NICE_QUESTION_VOTES_UP)

class GoodAnswerBadge(NodeCountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Answer voted up %s times') % str(settings.GOOD_ANSWER_VOTES_UP)

    def __init__(self):
        super(GoodAnswerBadge, self).__init__("answer", 'vote_up_count', settings.GOOD_ANSWER_VOTES_UP)

class GoodQuestionBadge(NodeCountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Question voted up %s times') % str(settings.GOOD_QUESTION_VOTES_UP)

    def __init__(self):
        super(GoodQuestionBadge, self).__init__("question", 'vote_up_count', settings.GOOD_QUESTION_VOTES_UP)

class GreatAnswerBadge(NodeCountableAbstractBadge):
    type = const.GOLD_BADGE
    description = _('Answer voted up %s times') % str(settings.GREAT_ANSWER_VOTES_UP)

    def __init__(self):
        super(GreatAnswerBadge, self).__init__("answer", 'vote_up_count', settings.GREAT_ANSWER_VOTES_UP)

class GreatQuestionBadge(NodeCountableAbstractBadge):
    type = const.GOLD_BADGE
    description = _('Question voted up %s times') % str(settings.GREAT_QUESTION_VOTES_UP)

    def __init__(self):
        super(GreatQuestionBadge, self).__init__("question", 'vote_up_count', settings.GREAT_QUESTION_VOTES_UP)


class FavoriteQuestionBadge(PostCountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Question favorited by %s users') % str(settings.FAVORITE_QUESTION_FAVS)

    def __init__(self):
        super(FavoriteQuestionBadge, self).__init__(Question, 'favourite_count', settings.FAVORITE_QUESTION_FAVS)

class StellarQuestionBadge(PostCountableAbstractBadge):
    type = const.GOLD_BADGE
    description = _('Question favorited by %s users') % str(settings.STELLAR_QUESTION_FAVS)

    def __init__(self):
        super(StellarQuestionBadge, self).__init__(Question, 'favourite_count', settings.STELLAR_QUESTION_FAVS)


class DisciplinedBadge(ActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Deleted own post with score of %s or higher') % str(settings.DISCIPLINED_MIN_SCORE)

    def __init__(self):
        def handler(instance):
            if instance.user.id == instance.content_object.author.id and instance.content_object.score >= settings.DISCIPLINED_MIN_SCORE:
                self.award_badge(instance.user, instance)

        super(DisciplinedBadge, self).__init__(const.TYPE_ACTIVITY_DELETE_QUESTION, handler)

class PeerPressureBadge(ActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Deleted own post with score of %s or lower') % str(settings.PEER_PRESSURE_MAX_SCORE)

    def __init__(self):
        def handler(instance):
            if instance.user.id == instance.content_object.author.id and instance.content_object.score <= settings.PEER_PRESSURE_MAX_SCORE:
                self.award_badge(instance.user, instance)

        super(PeerPressureBadge, self).__init__(const.TYPE_ACTIVITY_DELETE_QUESTION, handler)


class CitizenPatrolBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First flagged post')

    def __init__(self):
        super(CitizenPatrolBadge, self).__init__(const.TYPE_ACTIVITY_MARK_OFFENSIVE)

class CriticBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First down vote')

    def __init__(self):
        super(CriticBadge, self).__init__(const.TYPE_ACTIVITY_VOTE_DOWN)

class OrganizerBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First retag')

    def __init__(self):
        super(OrganizerBadge, self).__init__(const.TYPE_ACTIVITY_UPDATE_TAGS)

class SupporterBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First up vote')

    def __init__(self):
        super(SupporterBadge, self).__init__(const.TYPE_ACTIVITY_VOTE_UP)

class EditorBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First edit')

    def __init__(self):
        super(EditorBadge, self).__init__((const.TYPE_ACTIVITY_UPDATE_ANSWER, const.TYPE_ACTIVITY_UPDATE_QUESTION))

class ScholarBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First accepted answer on your own question')

    def __init__(self):
        super(ScholarBadge, self).__init__(const.TYPE_ACTIVITY_MARK_ANSWER)

class AutobiographerBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Completed all user profile fields')

    def __init__(self):
        super(AutobiographerBadge, self).__init__(const.TYPE_ACTIVITY_USER_FULL_UPDATED)

class CleanupBadge(FirstActivityAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('First rollback')

    def __init__(self):
        super(CleanupBadge, self).__init__((const.TYPE_ACTIVITY_CANCEL_VOTE_UP, const.TYPE_ACTIVITY_CANCEL_VOTE_DOWN))


class CivicDutyBadge(ActivityCountAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Voted %s times') % str(settings.CIVIC_DUTY_VOTES)

    def __init__(self):
        super(CivicDutyBadge, self).__init__((const.TYPE_ACTIVITY_VOTE_DOWN, const.TYPE_ACTIVITY_VOTE_UP), settings.CIVIC_DUTY_VOTES)

class PunditBadge(ActivityCountAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Left %s comments') % str(settings.PUNDIT_COMMENT_COUNT)

    def __init__(self):
        super(PunditBadge, self).__init__((const.TYPE_ACTIVITY_COMMENT_ANSWER, const.TYPE_ACTIVITY_COMMENT_QUESTION), settings.PUNDIT_COMMENT_COUNT)


class SelfLearnerBadge(CountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Answered your own question with at least %s up votes') % str(settings.SELF_LEARNER_UP_VOTES)

    def __init__(self):

        def handler(instance):
            if instance.node_type == "answer" and instance.author_id == instance.question.author_id:
                self.award_badge(instance.author, instance)

        super(SelfLearnerBadge, self).__init__(Node, 'vote_up_count', settings.SELF_LEARNER_UP_VOTES, handler)


class StrunkAndWhiteBadge(ActivityCountAbstractBadge):
    type = const.SILVER_BADGE
    name = _('Strunk & White')
    description = _('Edited %s entries') % str(settings.STRUNK_AND_WHITE_EDITS)

    def __init__(self):
        super(StrunkAndWhiteBadge, self).__init__((const.TYPE_ACTIVITY_UPDATE_ANSWER, const.TYPE_ACTIVITY_UPDATE_QUESTION), settings.STRUNK_AND_WHITE_EDITS)


def is_user_first(post):
    return post.__class__.objects.filter(author=post.author).order_by('added_at')[0].id == post.id

class StudentBadge(CountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Asked first question with at least one up vote')

    def __init__(self):
        def handler(instance):
            if instance.node_type == "question" and is_user_first(instance):
                self.award_badge(instance.author, instance)

        super(StudentBadge, self).__init__(Node, 'vote_up_count', 1, handler)

class TeacherBadge(CountableAbstractBadge):
    type = const.BRONZE_BADGE
    description = _('Answered first question with at least one up vote')

    def __init__(self):
        def handler(instance):
            if instance.node_type == "answer" and is_user_first(instance):
                self.award_badge(instance.author, instance)

        super(TeacherBadge, self).__init__(Node, 'vote_up_count', 1, handler)


class AcceptedAndVotedAnswerAbstractBadge(AbstractBadge):
    def __init__(self, up_votes, handler):
        def wrapper(sender, instance, **kwargs):
            if sender is Answer:
                if (not kwargs['field'] == "score") or (kwargs['new'] < kwargs['old']):
                    return

                answer = instance.leaf
                vote_count = kwargs['new']
            else:
                answer = instance.content_object
                vote_count = answer.vote_up_count

            if answer.accepted and vote_count == up_votes:
                handler(answer)

        activity_record.connect(wrapper, sender=const.TYPE_ACTIVITY_MARK_ANSWER, weak=False)
        denorm_update.connect(wrapper, sender=Node, weak=False)


class EnlightenedBadge(AcceptedAndVotedAnswerAbstractBadge):
    type = const.SILVER_BADGE
    description = _('First answer was accepted with at least %s up votes') % str(settings.ENLIGHTENED_UP_VOTES)

    def __init__(self):
        def handler(answer):
            self.award_badge(answer.author, answer, True)

        super(EnlightenedBadge, self).__init__(settings.ENLIGHTENED_UP_VOTES, handler)


class GuruBadge(AcceptedAndVotedAnswerAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Accepted answer and voted up %s times') % str(settings.GURU_UP_VOTES)

    def __init__(self):
        def handler(answer):
            self.award_badge(answer.author, answer)

        super(GuruBadge, self).__init__(settings.GURU_UP_VOTES, handler)


class NecromancerBadge(CountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Answered a question more than %(dif_days)s days later with at least %(up_votes)s votes') % \
            {'dif_days': str(settings.NECROMANCER_DIF_DAYS), 'up_votes': str(settings.NECROMANCER_UP_VOTES)}

    def __init__(self):
        def handler(instance):
            if instance.node_type == "answer" and instance.added_at >= (instance.question.added_at + timedelta(days=int(settings.NECROMANCER_DIF_DAYS))):
                self.award_badge(instance.author, instance)

        super(NecromancerBadge, self).__init__(Node, "vote_up_count", settings.NECROMANCER_UP_VOTES, handler)


class TaxonomistBadge(AbstractBadge):
    type = const.SILVER_BADGE
    description = _('Created a tag used by %s questions') % str(settings.TAXONOMIST_USE_COUNT)

    def __init__(self):
        def handler(instance, **kwargs):
            if instance.used_count == settings.TAXONOMIST_USE_COUNT:
                self.award_badge(instance.created_by, instance)           

        post_save.connect(handler, sender=Tag, weak=False)


#class GeneralistTag(AbstractBadge):
#    pass

#class ExpertTag(AbstractBadge):
#    pass

#class YearlingTag(AbstractBadge):
#    pass


            
