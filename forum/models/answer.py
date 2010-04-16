from base import *

from question import Question

class Answer(QandA):
    accepted    = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(User, null=True)

    class Meta(QandA.Meta):
        db_table = u'answer'

    @property
    def headline(self):
        return self.question.headline

    def mark_accepted(self, user):
        if not self.accepted and not self.question.answer_accepted:
            self.accepted = True
            self.accepted_at = datetime.datetime.now()
            self.accepted_by = user
            self.save()
            self.question.accepted_answer = self
            self.question.save()
            answer_accepted.send(sender=Answer, answer=self, user=user)
            return True

        return False

    def unmark_accepted(self, user):
        if self.accepted:
            self.accepted = False
            self.save()
            self.question.accepted_answer = None
            self.question.save()
            answer_accepted_canceled.send(sender=Answer, answer=self, user=user)
            return True

        return False

    def _update_question_answer_count(self, diff):
        self.question.answer_count = self.question.answer_count + diff
        self.question.save()

    def activate_revision(self, user, revision):
        super(Answer, self).activate_revision(user, revision)
        self.question.update_last_activity(user)

    def mark_deleted(self, user):
        if super(Answer, self).mark_deleted(user):
            self._update_question_answer_count(-1)

    def unmark_deleted(self):
        if super(Answer, self).unmark_deleted():
            self._update_question_answer_count(1)

    def get_latest_revision(self):
        return self.revisions.all()[0]

    def get_question_title(self):
        return self.question.title

    def get_absolute_url(self):
        return '%s#%s' % (self.question.get_absolute_url(), self.id)

    def save(self, *args, **kwargs):
        super(Answer, self).save(*args, **kwargs)

        if self._is_new:
            self._update_question_answer_count(1)

    def __unicode__(self):
        return self.html
        
answer_accepted = django.dispatch.Signal(providing_args=['answer', 'user'])
answer_accepted_canceled = django.dispatch.Signal(providing_args=['answer', 'user'])

class AnswerRevision(NodeRevision):
    class Meta:
        proxy = True