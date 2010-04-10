import re

from forum.badges.base import AbstractBadge
from forum.modules import get_modules_script_classes

ALL_BADGES = [
            cls() for name, cls
            in get_modules_script_classes('badges', AbstractBadge).items()
            if not re.search('AbstractBadge$', name)
        ]
