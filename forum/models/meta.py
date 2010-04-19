from base import *

class Vote(MetaContent, CancelableContent, UserContent):
    VOTE_UP = +1
    VOTE_DOWN = -1
    VOTE_CHOICES = (
        (VOTE_UP,   u'Up'),
        (VOTE_DOWN, u'Down'),
    )

    vote           = models.SmallIntegerField(choices=VOTE_CHOICES)
    voted_at       = models.DateTimeField(default=datetime.datetime.now)

    active = ActiveObjectManager()

    class Meta(MetaContent.Meta):
        db_table = u'vote'

    def __unicode__(self):
        return '[%s] voted at %s: %s' %(self.user, self.voted_at, self.vote)

    def _update_post_vote_count(self, diff):
        post = self.node.leaf
        field = self.vote == 1 and 'vote_up_count' or 'vote_down_count'
        post.__dict__[field] = post.__dict__[field] + diff
        post.save()

    def cancel(self):
        if super(Vote, self).cancel():
            self._update_post_vote_count(-1)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        if self._is_new:
            self._update_post_vote_count(1)

    def is_upvote(self):
        return self.vote == self.VOTE_UP

    def is_downvote(self):
        return self.vote == self.VOTE_DOWN


class FlaggedItem(MetaContent, UserContent):
    flagged_at     = models.DateTimeField(default=datetime.datetime.now)
    reason         = models.CharField(max_length=300, null=True)
    canceled       = models.BooleanField(default=False)

    active = ActiveObjectManager()

    class Meta(MetaContent.Meta):
        db_table = u'flagged_item'

    def __unicode__(self):
        return '[%s] flagged at %s' %(self.user, self.flagged_at)

    def _update_post_flag_count(self, diff):
        post = self.node
        post.offensive_flag_count = post.offensive_flag_count + diff
        post.save()

    def save(self, *args, **kwargs):
        super(FlaggedItem, self).save(*args, **kwargs)
        if self._is_new:
            self._update_post_flag_count(1)

    def cancel(self):
        if not self.canceled:
            self.canceled = True
            self.save()
            self._update_post_flag_count(-1)
            



