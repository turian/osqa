import os.path
from base import Setting, SettingSet
from forms import ImageFormWidget

from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

INTERNAL_VERSION = Setting('INTERNAL_VERSION', "59")
SETTINGS_PACK = Setting('SETTINGS_PACK', "default")

from basic import *
from email import *
from extkeys import *
from minrep import *
from repgain import *
from voting import *
from upload import *
from about import *
from faq import *
from form import *

BADGES_SET = SettingSet('badges', _('Badges config'), _("Configure badges on your OSQA site."), 500)

#__all__ = locals().keys()

