import datetime
import hashlib
from urllib import quote_plus, urlencode
from django.db import models, IntegrityError, connection, transaction
from django.utils.http import urlquote  as django_urlquote
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.db.models.signals import post_delete, post_save, pre_save, pre_delete
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.sitemaps import ping_google
import django.dispatch
from django.conf import settings
from forum import const
import logging

from forum.const import *

class CachedManager(models.Manager):
    use_for_related_fields = True

    def get(self, *args, **kwargs):
        try:
            pk = [v for (k,v) in kwargs.items() if k in ('pk', 'pk__exact', 'id', 'id__exact') or k.endswith('_ptr__pk')][0]
        except:
            pk = None

        if pk is not None:
            key = self.model.cache_key(pk)
            obj = cache.get(key)

            if obj is None:
                obj = super(CachedManager, self).get(*args, **kwargs)
                cache.set(key, obj, 60 * 60)

            return obj
        
        return super(CachedManager, self).get(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return super(CachedManager, self).get_or_create(*args, **kwargs)


class BaseModel(models.Model):
    objects = CachedManager()

    class Meta:
        abstract = True
        app_label = 'forum'

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self._original_state = dict([(k, v) for k,v in self.__dict__.items() if not k in kwargs])

    @classmethod
    def cache_key(cls, pk):
        return '%s.%s:%s' % (settings.APP_URL, cls.__name__, pk)

    def get_dirty_fields(self):
        missing = object()
        return dict([(k, self._original_state.get(k, None)) for k,v in self.__dict__.items()
                 if self._original_state.get(k, missing) == missing or self._original_state[k] != v])

    def save(self, *args, **kwargs):
        super(BaseModel, self).save(*args, **kwargs)
        self._original_state = dict(self.__dict__)
        cache.set(self.cache_key(self.pk), self, 86400)

    def delete(self):
        cache.delete(self.cache_key(self.pk))
        super(BaseModel, self).delete()


class ActiveObjectManager(models.Manager):
    def get_query_set(self):
        return super(ActiveObjectManager, self).get_query_set().filter(canceled=False)

class UndeletedObjectManager(models.Manager):
    def get_query_set(self):
        return super(UndeletedObjectManager, self).get_query_set().filter(deleted=False)

class MetaContent(BaseModel):
    """
        Base class for Vote, Comment and FlaggedItem
    """
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        app_label = 'forum'

from user import User

class UserContent(models.Model):
    user = models.ForeignKey(User, related_name='%(class)ss')

    class Meta:
        abstract = True
        app_label = 'forum'


marked_deleted = django.dispatch.Signal(providing_args=["instance", "deleted_by"])

class DeletableContent(models.Model):
    deleted     = models.BooleanField(default=False)
    deleted_at  = models.DateTimeField(null=True, blank=True)
    deleted_by  = models.ForeignKey(User, null=True, blank=True, related_name='deleted_%(class)ss')

    active = UndeletedObjectManager()

    class Meta:
        abstract = True
        app_label = 'forum'

    def mark_deleted(self, user):
        if not self.deleted:
            self.deleted = True
            self.deleted_at = datetime.datetime.now()
            self.deleted_by = user
            self.save()
            marked_deleted.send(sender=self.__class__, instance=self, deleted_by=user)
            return True
        else:
            return False

    def unmark_deleted(self):
        if self.deleted:
            self.deleted = False
            self.save()
            return True
        else:
            return False


class ContentRevision(models.Model):
    """
        Base class for QuestionRevision and AnswerRevision
    """
    revision   = models.PositiveIntegerField()
    author     = models.ForeignKey(User, related_name='%(class)ss')
    revised_at = models.DateTimeField()
    summary    = models.CharField(max_length=300, blank=True)
    text       = models.TextField()

    class Meta:
        abstract = True
        app_label = 'forum'


class AnonymousContent(models.Model):
    """
        Base class for AnonymousQuestion and AnonymousAnswer
    """
    session_key = models.CharField(max_length=40)  #session id for anonymous questions
    wiki = models.BooleanField(default=False)
    added_at = models.DateTimeField(default=datetime.datetime.now)
    ip_addr = models.IPAddressField(max_length=21) #allow high port numbers
    author = models.ForeignKey(User,null=True)
    text = models.TextField()
    summary = models.CharField(max_length=180)

    class Meta:
        abstract = True
        app_label = 'forum'


from meta import Comment, Vote, FlaggedItem
from user import activity_record

class Content(BaseModel, DeletableContent):
    """
        Base class for Question and Answer
    """
    author               = models.ForeignKey(User, related_name='%(class)ss')
    added_at             = models.DateTimeField(default=datetime.datetime.now)

    wiki                 = models.BooleanField(default=False)
    wikified_at          = models.DateTimeField(null=True, blank=True)

    #locked               = models.BooleanField(default=False)
    #locked_by            = models.ForeignKey(User, null=True, blank=True, related_name='locked_%(class)ss')
    #locked_at            = models.DateTimeField(null=True, blank=True)

    score                = models.IntegerField(default=0)
    vote_up_count        = models.IntegerField(default=0)
    vote_down_count      = models.IntegerField(default=0)

    comment_count        = models.PositiveIntegerField(default=0)
    offensive_flag_count = models.SmallIntegerField(default=0)

    last_edited_at       = models.DateTimeField(null=True, blank=True)
    last_edited_by       = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_%(class)ss')

    html                 = models.TextField()
    comments             = generic.GenericRelation(Comment)
    votes                = generic.GenericRelation(Vote)
    flagged_items        = generic.GenericRelation(FlaggedItem)

    class Meta:
        abstract = True
        app_label = 'forum'

    def save(self, *args, **kwargs):
        self.__dict__['score'] = self.__dict__['vote_up_count'] - self.__dict__['vote_down_count']
        super(Content,self).save(*args, **kwargs)

        try:
            ping_google()
        except Exception:
            logging.debug('problem pinging google did you register you sitemap with google?')


    def post_get_last_update_info(self):
            when = self.added_at
            who = self.author
            if self.last_edited_at and self.last_edited_at > when:
                when = self.last_edited_at
                who = self.last_edited_by
            comments = self.comments.all()
            if len(comments) > 0:
                for c in comments:
                    if c.added_at > when:
                        when = c.added_at
                        who = c.user
            return when, who