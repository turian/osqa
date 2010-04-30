from base import Setting, SettingSet
from django.forms.widgets import Textarea

FAQ_SET = SettingSet('faq', 'FAQ page', "Define the text in the about page. You can use markdown and some basic html tags.", 2000, True)

FAQ_PAGE_TEXT = Setting('FAQ_PAGE_TEXT',
"""

""", FAQ_SET, dict(
label = "FAQ page text",
help_text = " The faq page. ",
widget=Textarea(attrs={'rows': '25'})))