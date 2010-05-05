from django.core.management.base import NoArgsCommand

from forum.settings.base import BaseSetting
import forum.settings

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        values = {}
        for k in dir(forum.settings):
            v = forum.settings.__dict__[k]
            if not isinstance(v, BaseSetting): continue
            values[k] = {"default": v.default, "value": v.value}
            print '%s:' % `k`, values[k]

#        print values
#        print EMAIL_SUBJECT_PREFIX.value
