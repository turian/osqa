from base import *
from tag import Tag

class QuestionManager(CachedManager):
    def create_new(self, title=None,author=None,added_at=None, wiki=False,tagnames=None,summary=None, text=None):

        question = Question(
            title            = title,
            author           = author,
            added_at         = added_at,
            last_activity_at = added_at,
            last_activity_by = author,
            wiki             = wiki,
            tagnames         = tagnames,
            html             = text,
            summary          = summary
        )
        if question.wiki:
            question.last_edited_by = question.author
            question.last_edited_at = added_at
            question.wikified_at = added_at

        question.save()

        # create the first revision
        QuestionRevision.objects.create(
            question   = question,
            revision   = 1,
            title      = question.title,
            author     = author,
            revised_at = added_at,
            tagnames   = question.tagnames,
            summary    = CONST['default_version'],
            text       = text
        )
        return question

question_view = django.dispatch.Signal(providing_args=['instance', 'user'])

class Question(Content):
    title    = models.CharField(max_length=300)
    tags     = models.ManyToManyField(Tag, related_name='questions')
    answer_accepted = models.BooleanField(default=False)
    closed          = models.BooleanField(default=False)
    closed_by       = models.ForeignKey(User, null=True, blank=True, related_name='closed_questions')
    closed_at       = models.DateTimeField(null=True, blank=True)
    close_reason    = models.SmallIntegerField(choices=CLOSE_REASONS, null=True, blank=True)
    followed_by     = models.ManyToManyField(User, related_name='followed_questions')
    subscribers     = models.ManyToManyField(User, related_name='subscriptions', through='QuestionSubscription')

    # Denormalised data
    answer_count         = models.PositiveIntegerField(default=0)
    view_count           = models.IntegerField(default=0)
    favourite_count      = models.IntegerField(default=0)
    last_activity_at     = models.DateTimeField(default=datetime.datetime.now)
    last_activity_by     = models.ForeignKey(User, related_name='last_active_in_questions')
    tagnames             = models.CharField(max_length=125)
    summary              = models.CharField(max_length=180)

    favorited_by         = models.ManyToManyField(User, through='FavoriteQuestion', related_name='favorite_questions') 

    objects = QuestionManager()

    class Meta(Content.Meta):
        db_table = u'question'

    def delete(self):
        super(Question, self).delete()
        try:
            ping_google()
        except Exception:
            logging.debug('problem pinging google did you register you sitemap with google?')

    def get_tag_list_if_changed(self):
        dirty = self.get_dirty_fields()

        if 'tagnames' in dirty:
            new_tags = self.tagname_list()

            old_tags = dirty['tagnames']
            if old_tags is None:
                old_tags = []
            else:
                old_tags = [name for name in dirty['tagnames'].split(u' ')]

            tag_list = []

            for name in new_tags:
                try:
                    tag = Tag.objects.get(name=name)
                except:
                    tag = Tag.objects.create(name=name, created_by=self.last_edited_by or self.author)

                tag_list.append(tag)

                if not name in old_tags:
                    tag.used_count = tag.used_count + 1
                    if tag.deleted:
                        tag.unmark_deleted()
                    tag.save()

            for name in [n for n in old_tags if not n in new_tags]:
                tag = Tag.objects.get(name=name)
                tag.used_count = tag.used_count - 1
                if tag.used_count == 0:
                    tag.mark_deleted(self.last_edited_by or self.author)
                tag.save()

            return tag_list

        return None

    def save(self, *args, **kwargs):
        tags = self.get_tag_list_if_changed()
        super(Question, self).save(*args, **kwargs)
        if not tags is None: self.tags = tags

    def tagname_list(self):
        """Creates a list of Tag names from the ``tagnames`` attribute."""
        return [name for name in self.tagnames.split(u' ')]

    def tagname_meta_generator(self):
        return u','.join([unicode(tag) for tag in self.tagname_list()])

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

    def get_latest_revision(self):
        return self.revisions.all()[0]

    def get_last_update_info(self):
        when, who = self.post_get_last_update_info()

        answers = self.answers.all()
        if len(answers) > 0:
            for a in answers:
                a_when, a_who = a.post_get_last_update_info()
                if a_when > when:
                    when = a_when
                    who = a_who

        return when, who

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
    """A favorite Question of a User."""
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

class QuestionRevision(ContentRevision):
    """A revision of a Question."""
    question   = models.ForeignKey(Question, related_name='revisions')
    title      = models.CharField(max_length=300)
    tagnames   = models.CharField(max_length=125)

    class Meta(ContentRevision.Meta):
        db_table = u'question_revision'
        ordering = ('-revision',)

    def get_question_title(self):
        return self.question.title

    def get_absolute_url(self):
        #print 'in QuestionRevision.get_absolute_url()'
        return reverse('question_revisions', args=[self.question.id])

    def save(self, *args, **kwargs):
        """Looks up the next available revision number."""
        if not self.revision:
            self.revision = QuestionRevision.objects.filter(
                question=self.question).values_list('revision',
                                                    flat=True)[0] + 1
        super(QuestionRevision, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'revision %s of %s' % (self.revision, self.title)

class AnonymousQuestion(AnonymousContent):
    title = models.CharField(max_length=300)
    tagnames = models.CharField(max_length=125)

    def publish(self,user):
        added_at = datetime.datetime.now()
        Question.objects.create_new(title=self.title, author=user, added_at=added_at,
                                wiki=self.wiki, tagnames=self.tagnames,
                                summary=self.summary, text=self.text)
        self.delete()

from answer import Answer, AnswerManager
