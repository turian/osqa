from django.core.management.base import BaseCommand

from forum.settings.base import BaseSetting
import forum.settings

class Command(BaseCommand):
    help = 'Set one setting of the web admin interface'
    args = 'settingname newvalue'

    def handle(self, *args, **options):
        assert len(args) == 2

        settingname = args[0]
        newvalue = args[1]
        print "Old value of %s: %s" % (settingname, `forum.settings.__dict__[settingname].value`)
        forum.settings.__dict__[settingname].set_value(newvalue)
        print "New value of %s: %s" % (settingname, `forum.settings.__dict__[settingname].value`)
