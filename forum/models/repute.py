from base import *
from django.contrib.contenttypes.models import ContentType
from forum.models import User

from django.utils.translation import ugettext as _

class Badge(BaseModel):
    """Awarded for notable actions performed on the site by Users."""
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    TYPE_CHOICES = (
        (GOLD,   _('gold')),
        (SILVER, _('silver')),
        (BRONZE, _('bronze')),
    )

    name        = models.CharField(max_length=50)
    type        = models.SmallIntegerField(choices=TYPE_CHOICES)
    slug        = models.SlugField(max_length=50, blank=True)
    description = models.CharField(max_length=300)
    multiple    = models.BooleanField(default=False)
    # Denormalised data
    awarded_count = models.PositiveIntegerField(default=0)
    awarded_to    = models.ManyToManyField(User, through='Award', related_name='badges')

    class Meta:
        app_label = 'forum'
        db_table = u'badge'
        ordering = ('name',)
        unique_together = ('name', 'type')

    def __unicode__(self):
        return u'%s: %s' % (self.get_type_display(), self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name#slugify(self.name)
        super(Badge, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '%s%s/' % (reverse('badge', args=[self.id]), self.slug)


class AwardManager(models.Manager):
    def get_recent_awards(self):
        awards = super(AwardManager, self).extra(
            select={'badge_id': 'badge.id', 'badge_name':'badge.name',
                          'badge_description': 'badge.description', 'badge_type': 'badge.type',
                          'user_id': 'auth_user.id', 'user_name': 'auth_user.username'
                          },
            tables=['award', 'badge', 'auth_user'],
            order_by=['-awarded_at'],
            where=['auth_user.id=award.user_id AND badge_id=badge.id'],
        ).values('badge_id', 'badge_name', 'badge_description', 'badge_type', 'user_id', 'user_name')
        return awards

class Award(GenericContent, UserContent):
    """The awarding of a Badge to a User."""
    badge      = models.ForeignKey('Badge', related_name='award_badge')
    awarded_at = models.DateTimeField(default=datetime.datetime.now)
    notified   = models.BooleanField(default=False)

    objects = AwardManager()

    def __unicode__(self):
        return u'[%s] is awarded a badge [%s] at %s' % (self.user.username, self.badge.name, self.awarded_at)

    def save(self, *args, **kwargs):
        super(Award, self).save(*args, **kwargs)

        if self._is_new:
            self.badge.awarded_count += 1
            self.badge.save()

            if self.badge.type == Badge.GOLD:
                self.user.gold += 1
            if self.badge.type == Badge.SILVER:
                self.user.silver += 1
            if self.badge.type == Badge.BRONZE:
                self.user.bronze += 1
            self.user.save()

    class Meta:
        unique_together = ('content_type', 'object_id', 'user', 'badge')
        app_label = 'forum'
        db_table = u'award'


class Repute(MetaContent, CancelableContent, UserContent):
    value    = models.SmallIntegerField(default=0)
    question = models.ForeignKey('Question')
    reputed_at = models.DateTimeField(default=datetime.datetime.now)
    reputation_type = models.SmallIntegerField(choices=TYPE_REPUTATION)
    user_previous_rep = models.IntegerField(default=0)

    def __unicode__(self):
        return u'[%s]\' reputation changed at %s' % (self.user.username, self.reputed_at)

    @property
    def positive(self):
        if self.value > 0: return self.value
        return 0

    @property
    def negative(self):
        if self.value < 0: return self.value
        return 0

    @property
    def reputation(self):
        return self.user_previous_rep + self.value

    def cancel(self):
        if super(Repute, self).cancel():
            self.user.reputation = self.user.reputation - self.value
            self.user.save()

    def save(self, *args, **kwargs):
        self.user_previous_rep = self.user.reputation
        self.user.reputation = self.user.reputation + self.value
        self.user.save()
        super(Repute, self).save(*args, **kwargs)

    class Meta:
        app_label = 'forum'
        db_table = u'repute'
