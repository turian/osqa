# encoding:utf-8
from django.utils.translation import ugettext as _
"""
All constants could be used in other modules
For reasons that models, views can't have unicode text in this project, all unicode text go here.
"""
CLOSE_REASONS = (
    (1, _('duplicate question')),
    (2, _('question is off-topic or not relevant')),
    (3, _('too subjective and argumentative')),
    (4, _('is not an answer to the question')),
    (5, _('the question is answered, right answer was accepted')),
    (6, _('problem is not reproducible or outdated')),
    (7, _('question contains offensive inappropriate, or malicious remarks')),
    (8, _('spam or advertising')),
)

TYPE_REPUTATION_GAIN_BY_UPVOTED = 1
TYPE_REPUTATION_GAIN_BY_ANSWER_ACCEPTED = 2
TYPE_REPUTATION_GAIN_BY_ACCEPTING_ANSWER = 3
TYPE_REPUTATION_GAIN_BY_DOWNVOTE_CANCELED = 4
TYPE_REPUTATION_GAIN_BY_CANCELING_DOWNVOTE = 5
TYPE_REPUTATION_LOST_BY_CANCELLING_ACCEPTED_ANSWER = -1
TYPE_REPUTATION_LOST_BY_ACCEPTED_ANSWER_CANCELED = -2
TYPE_REPUTATION_LOST_BY_DOWNVOTED = -3
TYPE_REPUTATION_LOST_BY_FLAGGED = -4
TYPE_REPUTATION_LOST_BY_DOWNVOTING = -5
TYPE_REPUTATION_LOST_BY_FLAGGED_3_TIMES = -6
TYPE_REPUTATION_LOST_BY_FLAGGED_5_TIMES = -7
TYPE_REPUTATION_LOST_BY_UPVOTE_CANCELED = -8

TYPE_REPUTATION = (
    (TYPE_REPUTATION_GAIN_BY_UPVOTED, 'gain_by_upvoted'),
    (TYPE_REPUTATION_GAIN_BY_ANSWER_ACCEPTED, 'gain_by_answer_accepted'),
    (TYPE_REPUTATION_GAIN_BY_ACCEPTING_ANSWER, 'gain_by_accepting_answer'),
    (TYPE_REPUTATION_GAIN_BY_DOWNVOTE_CANCELED, 'gain_by_downvote_canceled'),
    (TYPE_REPUTATION_GAIN_BY_CANCELING_DOWNVOTE, 'gain_by_canceling_downvote'),
    (TYPE_REPUTATION_LOST_BY_CANCELLING_ACCEPTED_ANSWER, 'lose_by_canceling_accepted_answer'),
    (TYPE_REPUTATION_LOST_BY_ACCEPTED_ANSWER_CANCELED, 'lose_by_accepted_answer_cancled'),
    (TYPE_REPUTATION_LOST_BY_DOWNVOTED, 'lose_by_downvoted'),
    (TYPE_REPUTATION_LOST_BY_FLAGGED, 'lose_by_flagged'),
    (TYPE_REPUTATION_LOST_BY_DOWNVOTING, 'lose_by_downvoting'),
    (TYPE_REPUTATION_LOST_BY_FLAGGED_3_TIMES, 'lose_by_flagged_lastrevision_3_times'),
    (TYPE_REPUTATION_LOST_BY_FLAGGED_5_TIMES, 'lose_by_flagged_lastrevision_5_times'),
    (TYPE_REPUTATION_LOST_BY_UPVOTE_CANCELED, 'lose_by_upvote_canceled'),
)

TYPE_ACTIVITY_ASK_QUESTION=1
TYPE_ACTIVITY_ANSWER=2
TYPE_ACTIVITY_COMMENT_QUESTION=3
TYPE_ACTIVITY_COMMENT_ANSWER=4
TYPE_ACTIVITY_UPDATE_QUESTION=5
TYPE_ACTIVITY_UPDATE_ANSWER=6
TYPE_ACTIVITY_PRIZE=7
TYPE_ACTIVITY_MARK_ANSWER=8
TYPE_ACTIVITY_VOTE_UP=9
TYPE_ACTIVITY_VOTE_DOWN=10
TYPE_ACTIVITY_CANCEL_VOTE_UP=11
TYPE_ACTIVITY_CANCEL_VOTE_DOWN=19
TYPE_ACTIVITY_DELETE_QUESTION=12
TYPE_ACTIVITY_DELETE_ANSWER=13
TYPE_ACTIVITY_MARK_OFFENSIVE=14
TYPE_ACTIVITY_UPDATE_TAGS=15
TYPE_ACTIVITY_FAVORITE=16
TYPE_ACTIVITY_USER_FULL_UPDATED = 17
TYPE_ACTIVITY_QUESTION_EMAIL_UPDATE_SENT = 18
#TYPE_ACTIVITY_EDIT_QUESTION=17
#TYPE_ACTIVITY_EDIT_ANSWER=18

TYPE_ACTIVITY = (
    (TYPE_ACTIVITY_ASK_QUESTION, _('question')),
    (TYPE_ACTIVITY_ANSWER, _('answer')),
    (TYPE_ACTIVITY_COMMENT_QUESTION, _('commented question')),
    (TYPE_ACTIVITY_COMMENT_ANSWER, _('commented answer')),
    (TYPE_ACTIVITY_UPDATE_QUESTION, _('edited question')),
    (TYPE_ACTIVITY_UPDATE_ANSWER, _('edited answer')),
    (TYPE_ACTIVITY_PRIZE, _('received award')),
    (TYPE_ACTIVITY_MARK_ANSWER, _('marked best answer')),
    (TYPE_ACTIVITY_VOTE_UP, _('upvoted')),
    (TYPE_ACTIVITY_VOTE_DOWN, _('downvoted')),
    (TYPE_ACTIVITY_CANCEL_VOTE_UP, _('upvote canceled')),
    (TYPE_ACTIVITY_CANCEL_VOTE_DOWN, _('downvote canceled')),
    (TYPE_ACTIVITY_DELETE_QUESTION, _('deleted question')),
    (TYPE_ACTIVITY_DELETE_ANSWER, _('deleted answer')),
    (TYPE_ACTIVITY_MARK_OFFENSIVE, _('marked offensive')),
    (TYPE_ACTIVITY_UPDATE_TAGS, _('updated tags')),
    (TYPE_ACTIVITY_FAVORITE, _('selected favorite')),
    (TYPE_ACTIVITY_USER_FULL_UPDATED, _('completed user profile')),
    (TYPE_ACTIVITY_QUESTION_EMAIL_UPDATE_SENT, _('email update sent to user')),
)

TYPE_RESPONSE = {
    'QUESTION_ANSWERED' : _('question_answered'),
    'QUESTION_COMMENTED': _('question_commented'),
    'ANSWER_COMMENTED'  : _('answer_commented'),
    'ANSWER_ACCEPTED'   : _('answer_accepted'),
}

CONST = {
    'closed'            : _('[closed]'),
	'deleted'           : _('[deleted]'),
    'default_version'   : _('initial version'),
    'retagged'          : _('retagged'),
}

BRONZE_BADGE = 3
SILVER_BADGE = 2
GOLD_BADGE = 1

NOTIFICATION_CHOICES = (
    ('i', _('Instantly')),
    ('d', _('Daily')),
    ('w', _('Weekly')),
    ('n', _('No notifications')),
)
