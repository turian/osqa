import os.path

from base import Setting, SettingSet
from forms import ImageFormWidget

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Textarea

BASIC_SET = SettingSet('basic', _('Basic Settings'), _("The basic settings for your application"), 1)

APP_LOGO = Setting('APP_LOGO', '/m/default/media/images/logo.png', BASIC_SET, dict(
label = _("Application logo"),
help_text = _("Your site main logo."),
widget=ImageFormWidget))

APP_FAVICON = Setting('APP_FAVICON', '/m/default/media/images/favicon.ico', BASIC_SET, dict(
label = _("Favicon"),
help_text = _("Your site favicon."),
widget=ImageFormWidget))

APP_TITLE = Setting('APP_TITLE', 'OSQA: Open Source Q&A Forum', BASIC_SET, dict(
label = _("Application title"),
help_text = _("The title of your application that will show in the browsers title bar")))

APP_SHORT_NAME = Setting('APP_SHORT_NAME', 'OSQA', BASIC_SET, dict(
label = _("Application short name"),
help_text = "The short name for your application that will show up in many places."))

APP_KEYWORDS = Setting('APP_KEYWORDS', 'OSQA,CNPROG,forum,community', BASIC_SET, dict(
label = _("Application keywords"),
help_text = _("The meta keywords that will be available through the HTML meta tags.")))

APP_DESCRIPTION = Setting('APP_DESCRIPTION', 'Ask and answer questions.', BASIC_SET, dict(
label = _("Application description"),
help_text = _("The description of your application"),
widget=Textarea))

APP_INTRO = Setting('APP_INTRO', '<p>Ask and answer questions, make the world better!</p>', BASIC_SET, dict(
label = _("Application intro"),
help_text = _("The introductory page that is visible in the sidebar for anonymous users."),
widget=Textarea))

APP_COPYRIGHT = Setting('APP_COPYRIGHT', 'Copyright OSQA, 2010. Some rights reserved under creative commons license.', BASIC_SET, dict(
label = _("Copyright notice"),
help_text = _("The copyright notice visible at the footer of your page.")))