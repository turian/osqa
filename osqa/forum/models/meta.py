from base import *
import re

class Vote(MetaContent, UserContent):
    VOTE_UP = +1
    VOTE_DOWN = -1
    VOTE_CHOICES = (
        (VOTE_UP,   u'Up'),
        (VOTE_DOWN, u'Down'),
    )

    vote           = models.SmallIntegerField(choices=VOTE_CHOICES)
    voted_at       = models.DateTimeField(default=datetime.datetime.now)
    canceled       = models.BooleanField(default=False)

    active = ActiveObjectManager()

    class Meta(MetaContent.Meta):
        db_table = u'vote'

    def __unicode__(self):
        return '[%s] voted at %s: %s' %(self.user, self.voted_at, self.vote)

    def _update_post_vote_count(self, diff):
        post = self.content_object
        field = self.vote == 1 and 'vote_up_count' or 'vote_down_count'
        post.__dict__[field] = post.__dict__[field] + diff
        post.save()

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        if self._is_new:
            self._update_post_vote_count(1)

    def cancel(self):
        if not self.canceled:
            self.canceled = True
            self.save()
            self._update_post_vote_count(-1)
            vote_canceled.send(sender=Vote, instance=self)

    def is_upvote(self):
        return self.vote == self.VOTE_UP

    def is_downvote(self):
        return self.vote == self.VOTE_DOWN

vote_canceled = django.dispatch.Signal(providing_args=['instance'])

class FlaggedItem(MetaContent, UserContent):
    """A flag on a Question or Answer indicating offensive content."""
    flagged_at     = models.DateTimeField(default=datetime.datetime.now)
    reason         = models.CharField(max_length=300, null=True)
    canceled       = models.BooleanField(default=False)

    active = ActiveObjectManager()

    class Meta(MetaContent.Meta):
        db_table = u'flagged_item'

    def __unicode__(self):
        return '[%s] flagged at %s' %(self.user, self.flagged_at)

    def _update_post_flag_count(self, diff):
        post = self.content_object
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
            

class Comment(MetaContent, UserContent, DeletableContent):
    comment        = models.CharField(max_length=300)
    added_at       = models.DateTimeField(default=datetime.datetime.now)
    score          = models.IntegerField(default=0)
    liked_by       = models.ManyToManyField(User, through='LikedComment', related_name='comments_liked')

    class Meta(MetaContent.Meta):
        ordering = ('-added_at',)
        db_table = u'comment'

    def _update_post_comment_count(self, diff):
        post = self.content_object
        post.comment_count = post.comment_count + diff
        post.save()

    def save(self, *args, **kwargs):
        super(Comment,self).save(*args, **kwargs)

        if self._is_new:
            self._update_post_comment_count(1)

        try:
            ping_google()
        except Exception:
            logging.debug('problem pinging google did you register you sitemap with google?')

    def mark_deleted(self, user):
        if super(Comment, self).mark_deleted(user):
            self._update_post_comment_count(-1)

    def unmark_deleted(self):
        if super(Comment, self).unmark_deleted():
            self._update_post_comment_count(1)

    def is_reply_to(self, user):
        inreply = re.search('@\w+', self.comment)
        if inreply is not None:
            return user.username.startswith(inreply[1:])

        return False

    def __unicode__(self):
        return self.comment


class LikedComment(models.Model):
    comment       = models.ForeignKey(Comment)
    user          = models.ForeignKey(User)
    added_at      = models.DateTimeField(default=datetime.datetime.now)
    canceled      = models.BooleanField(default=False)

    active = ActiveObjectManager()

    class Meta:
        app_label = 'forum'

    def _update_comment_score(self, diff):
        self.comment.score = self.comment.score + diff
        self.comment.save()

    def save(self, *args, **kwargs):
        super(LikedComment, self).save(*args, **kwargs)
        if self._is_new:
            self._update_comment_score(1)

    def cancel(self):
        if not self.canceled:
            self.canceled = True
            self.save()
            self._update_comment_score(-1)


