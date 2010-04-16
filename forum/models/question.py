from base import *
from tag import Tag
from django.utils.translation import ugettext as _

question_view = django.dispatch.Signal(providing_args=['instance', 'user'])

class Question(QandA):
    accepted_answer = models.OneToOneField('Answer', null=True, related_name="question_accepting")
    closed          = models.BooleanField(default=False)
    closed_by       = models.ForeignKey(User, null=True, blank=True, related_name='closed_questions')
    closed_at       = models.DateTimeField(null=True, blank=True)
    close_reason    = models.SmallIntegerField(choices=CLOSE_REASONS, null=True, blank=True)
    subscribers     = models.ManyToManyField(User, related_name='subscriptions', through='QuestionSubscription')

    # Denormalised data
    answer_count         = models.PositiveIntegerField(default=0)
    view_count           = models.IntegerField(default=0)
    favourite_count      = models.IntegerField(default=0)
    last_activity_at     = models.DateTimeField(default=datetime.datetime.now)
    last_activity_by     = models.ForeignKey(User, related_name='last_active_in_questions', null=True)

    favorited_by         = models.ManyToManyField(User, through='FavoriteQuestion', related_name='favorite_questions')

    class Meta(QandA.Meta):
        db_table = u'question'

    @property
    def headline(self):
        if self.closed:
            return _('[closed] ') + self.title

        if self.deleted:
            return _('[deleted] ') + self.title

        return self.title

    @property
    def answer_accepted(self):
        return self.accepted_answer is not None

    def save(self, *args, **kwargs):
        if not self.last_activity_by:
            self.last_activity_by = self.author
        super(Question, self).save(*args, **kwargs)

    def update_last_activity(self, user):
        self.last_activity_by = user
        self.last_activity_at = datetime.datetime.now()
        self.save()

    def activate_revision(self, user, revision):
        super(Question, self).activate_revision(user, revision)
        self.update_last_activity(user)

    @models.permalink    
    def get_absolute_url(self):
        return ('question', (), {'id': self.id, 'slug': django_urlquote(slugify(self.title))})

    def get_answer_count_by_user(self, user_id):
        from answer import Answer
        query_set = Answer.objects.filter(author__id=user_id)
        return query_set.filter(question=self).count()

    def get_question_title(self):
        if self.closed:
            attr = CONST['closed']
        elif self.deleted:
            attr = CONST['deleted']
        else:
            attr = None
        if attr is not None:
            return u'%s %s' % (self.title, attr)
        else:
            return self.title

    def get_revision_url(self):
        return reverse('question_revisions', args=[self.id])

    def get_related_questions(self, count=10):
        cache_key = '%s.related_questions:%d:%d' % (settings.APP_URL, count, self.id)
        related_list = cache.get(cache_key)

        if related_list is None:
            related_list = Question.objects.values('id').filter(tags__id__in=[t.id for t in self.tags.all()]
            ).exclude(id=self.id).exclude(deleted=True).annotate(frequency=models.Count('id')).order_by('-frequency')[:count]
            cache.set(cache_key, related_list, 60 * 60)

        return [Question.objects.get(id=r['id']) for r in related_list]

    def __unicode__(self):
        return self.title

def question_viewed(instance, **kwargs):
    instance.view_count += 1
    instance.save()

question_view.connect(question_viewed)

class FavoriteQuestion(models.Model):
    question      = models.ForeignKey('Question')
    user          = models.ForeignKey(User, related_name='user_favorite_questions')
    added_at      = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = ('question', 'user')
        app_label = 'forum'
        db_table = u'favorite_question'

    def __unicode__(self):
        return '[%s] favorited at %s' %(self.user, self.added_at)

    def _update_question_fav_count(self, diff):
        self.question.favourite_count = self.question.favourite_count + diff
        self.question.save()

    def save(self, *args, **kwargs):
        super(FavoriteQuestion, self).save(*args, **kwargs)
        if self._is_new:
            self._update_question_fav_count(1)

    def delete(self):
        self._update_question_fav_count(-1)
        super(FavoriteQuestion, self).delete()

class QuestionSubscription(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    auto_subscription = models.BooleanField(default=True)
    last_view = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        app_label = 'forum'


class QuestionRevision(NodeRevision):
    class Meta:
        proxy = True
        
