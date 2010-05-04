from os import linesep
from csv import reader, QUOTE_NONE
import markdown
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re

#from django.conf import settings
from forum import settings

class SettingsExtension(markdown.Extension):
    def __init__(self, configs):
        self.configs = {} # settings.REP_TO_VOTE_UP}
        for key, value in configs:
            self.config[key] = value

        # self.extendMarkdown(markdown.Markdown()., config)

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('MinRep', SettingsPre(self), '_begin')

class SettingsPre(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:

            # tags relating to the minrip.py settings
            line = line.replace('REP_TO_VOTE_UP', '%d' % settings.REP_TO_VOTE_UP)
            line = line.replace('REP_TO_VOTE_DOWN', '%d' % settings.REP_TO_VOTE_DOWN)
            line = line.replace('REP_TO_FLAG', '%d' % settings.REP_TO_FLAG)
            line = line.replace('REP_TO_COMMENT', '%d' % settings.REP_TO_COMMENT)
            line = line.replace('REP_TO_LIKE_COMMENT', '%d' % settings.REP_TO_LIKE_COMMENT)
            line = line.replace('REP_TO_CLOSE_OWN', '%d' % settings.REP_TO_CLOSE_OWN)
            line = line.replace('REP_TO_REOPEN_OWN', '%d' % settings.REP_TO_REOPEN_OWN)
            line = line.replace('REP_TO_RETAG', '%d' % settings.REP_TO_RETAG)
            line = line.replace('REP_TO_EDIT_WIKI', '%d' % settings.REP_TO_EDIT_WIKI)
            line = line.replace('REP_TO_EDIT_OTHERS', '%d' % settings.REP_TO_EDIT_OTHERS)
            line = line.replace('REP_TO_CLOSE_OTHERS', '%d' % settings.REP_TO_CLOSE_OTHERS)
            line = line.replace('REP_TO_DELETE_COMMENTS', '%d' % settings.REP_TO_DELETE_COMMENTS)
            line = line.replace('REP_TO_VIEW_FLAGS', '%d' % settings.REP_TO_VIEW_FLAGS)

            new_lines.append(line)

        return new_lines

def makeSettingsExtension(configs={}) :
    return MinRepExtension(configs=configs)
