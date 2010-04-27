from base import *
import re

class Comment(Node):
    class Meta(Node.Meta):
        ordering = ('-added_at',)
        proxy = True

    def _update_parent_comment_count(self, diff):
        parent = self.parent
        parent.comment_count = parent.comment_count + diff
        parent.save()

    @property
    def comment(self):
        return self.body

    @property
    def headline(self):
        return self.absolute_parent.headline

    @property
    def content_object(self):
        return self.parent.leaf

    def save(self, *args, **kwargs):
        super(Comment,self).save(*args, **kwargs)

        if self._is_new:
            self._update_parent_comment_count(1)

        try:
            ping_google()
        except Exception:
            logging.debug('problem pinging google did you register your sitemap with google?')

    def mark_deleted(self, user):
        if super(Comment, self).mark_deleted(user):
            self._update_parent_comment_count(-1)

    def unmark_deleted(self):
        if super(Comment, self).unmark_deleted():
            self._update_parent_comment_count(1)

    def is_reply_to(self, user):
        inreply = re.search('@\w+', self.body)
        if inreply is not None:
            return user.username.startswith(inreply.group(0))

        return False

    def get_absolute_url(self):
        return self.absolute_parent.get_absolute_url() + "#%d" % self.id

    def __unicode__(self):
        return self.body

