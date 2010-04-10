from forum.badges.base import CountableAbstractBadge
from forum.models import Question, Tag
from forum import const
from django.utils.translation import ugettext as _
import settings

class BugBusterBadge(CountableAbstractBadge):
    type = const.SILVER_BADGE
    description = _('Got %s upvotes in a question tagged with "bug"') % str(settings.BUG_BUSTER_VOTES_UP)

    def __init__(self):

        def handler(instance):
            try:
                bug_tag = Tag.objects.get(name='bug')
                if bug_tag in instance.tags.all():
                    self.award_badge(instance.author, instance)
            except:
                pass

        super(BugBusterBadge, self).__init__(Question, 'vote_up_count', settings.BUG_BUSTER_VOTES_UP, handler)