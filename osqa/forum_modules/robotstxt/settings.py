from forum.settings.base import Setting, SettingSet
from django.forms.widgets import Textarea

ROBOTS_SET = SettingSet('robots', 'Robots txt', "Set up the robots.txt file.", 3000)

ROBOTS_FILE = Setting('ROBOTS_FILE',
"""
User-Agent: *
Disallow: /accounts/
Disallow: /users/
""", ROBOTS_SET, dict(
label = "Robots.txt file",
help_text = """
The robots.txt file search engine spiders will see.
""",
widget=Textarea(attrs={'rows': '20'})))