from base import *

from question import Question

class AnswerManager(CachedManager):
    def create_new(self, question=None, author=None, added_at=None, wiki=False, text='', email_notify=False):
        answer = Answer(
            question = question,
            author = author,
            added_at = added_at,
            wiki = wiki,
            html = text
        )
        if answer.wiki:
            answer.last_edited_by = answer.author
            answer.last_edited_at = added_at
            answer.wikified_at = added_at

        answer.save()

        #update question data
        question.last_activity_at = added_at
        question.last_activity_by = author
        question.save()

        AnswerRevision.objects.create(
            answer     = answer,
            revision   = 1,
            author     = author,
            revised_at = added_at,
            summary    = CONST['default_version'],
            text       = text
        )


class Answer(Content):
    question = models.ForeignKey('Question', related_name='answers')
    accepted    = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(User, null=True)


    objects = AnswerManager()

    class Meta(Content.Meta):
        db_table = u'answer'

    def mark_accepted(self, user):
        if not self.accepted and not self.question.answer_accepted:
            self.accepted = True
            self.accepted_at = datetime.datetime.now()
            self.accepted_by = user
            self.save()
            self.question.answer_accepted = True
            self.question.save()
            return True

        return False

    def unmark_accepted(self):
        if self.accepted:
            self.accepted = False
            self.save()
            self.question.answer_accepted = False
            self.question.save()
            return True

        return False

    def _update_question_answer_count(self, diff):
        self.question.answer_count = self.question.answer_count + diff
        self.question.save()

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
        

class AnswerRevision(ContentRevision):
    """A revision of an Answer."""
    answer     = models.ForeignKey('Answer', related_name='revisions')

    def get_absolute_url(self):
        return reverse('answer_revisions', kwargs={'id':self.answer.id})

    def get_question_title(self):
        return self.answer.question.title

    class Meta(ContentRevision.Meta):
        db_table = u'answer_revision'
        ordering = ('-revision',)

    def save(self, *args, **kwargs):
        """Looks up the next available revision number if not set."""
        if not self.revision:
            self.revision = AnswerRevision.objects.filter(
                answer=self.answer).values_list('revision',
                                                flat=True)[0] + 1
        super(AnswerRevision, self).save(*args, **kwargs)

class AnonymousAnswer(AnonymousContent):
    question = models.ForeignKey('Question', related_name='anonymous_answers')

    def publish(self,user):
        added_at = datetime.datetime.now()
        #print user.id
        Answer.objects.create_new(question=self.question,wiki=self.wiki,
                            added_at=added_at,text=self.text,
                            author=user)
        self.delete()
