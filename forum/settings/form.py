import os.path
from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

FORUM_SET = SettingSet('form', _('Form settings'), _("General settings for the OSQA forms."), 10)



""" settings for questions """
FORM_MIN_QUESTION_TITLE = Setting('FORM_MIN_QUESTION_TITLE', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a question's title"),
help_text = _("The minimum number of characters a user must enter into the title field of a question.")))

# FORM_MAX_QUESTION_TITLE = Setting('FORM_MAX_QUESTION_TITLE', 100, FORUM_SET, dict(
# label = _("Maximum number of characters for a question."),
# help_text = _("The maximum number of characters a user can enter into the description field to submit a question.")))

FORM_MIN_QUESTION_BODY = Setting('FORM_MIN_QUESTION_BODY', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a question's content"),
help_text = _("The minimum number of characters a user must enter into the content field of a question.")))

# FORM_MAX_QUESTION_DESCRIPTION = Setting('FORM_MAX_QUESTION_DESCRIPTION', 600, FORUM_SET, dict(
# label = _("Maximum number of characters for a question."),
# help_text = _("The maximum number of characters a user can enter into the description field to submit a question.")))

FORM_EMPTEY_QUESTION_BODY = Setting('FORM_EMPTY_QUESTION_BODY', False, FORUM_SET, dict(
label = _("Empty question content"),
help_text = _("If a question's content can be empty."),
required=False))



""" settings for comments """
FORM_MIN_COMMENT_BODY = Setting('FORM_MIN_COMMENT_BODY', 10, FORUM_SET, dict(
label = _("Minimum number of characters for a comment"),
help_text = _("The minimum number of characters a user must enter into the body of a comment.")))

FORM_MAX_COMMENT_BODY = Setting('FORM_MAX_COMMENT_BODY', 600, FORUM_SET, dict(
label = _("Maximum length of comment"),
help_text = _("The maximum number of characters a user can enter into the body of a comment.")))