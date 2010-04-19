import datetime
import re
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
    int_cache_re = re.compile('^_[\w_]+cache$')

    def cache_obj(self, obj):
        int_cache_keys = [k for k in obj.__dict__.keys() if self.int_cache_re.match(k)]

        for k in int_cache_keys:
            del obj.__dict__[k]

        cache.set(self.model.cache_key(obj.id), obj, 60 * 60)

    def get(self, *args, **kwargs):
        try:
            pk = [v for (k,v) in kwargs.items() if k in ('pk', 'pk__exact', 'id', 'id__exact'
                            ) or k.endswith('_ptr__pk') or k.endswith('_ptr__id')][0]
        except:
            pk = None

        if pk is not None:
            key = self.model.cache_key(pk)
            obj = cache.get(key)

            if obj is None:
                obj = super(CachedManager, self).get(*args, **kwargs)
                self.cache_obj(obj)
            else:
                d = obj.__dict__

            return obj
        
        return super(CachedManager, self).get(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except:
            return super(CachedManager, self).get_or_create(*args, **kwargs)

denorm_update = django.dispatch.Signal(providing_args=["instance", "field", "old", "new"])

class DenormalizedField(models.PositiveIntegerField):
    __metaclass__ = models.SubfieldBase

    def contribute_to_class(self, cls, name):
        super (DenormalizedField, self).contribute_to_class(cls, name)
        if not hasattr(cls, '_denormalizad_fields'):
            cls._denormalizad_fields = []

        cls._denormalizad_fields.append(name)

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
        put_back = None

        if hasattr(self.__class__, '_denormalizad_fields'):
            dirty = self.get_dirty_fields()
            put_back = [f for f in self.__class__._denormalizad_fields if f in dirty]

            if put_back:
                for n in put_back:
                    self.__dict__[n] = models.F(n) + (self.__dict__[n] - dirty[n])

        super(BaseModel, self).save(*args, **kwargs)

        if put_back:
            try:
                self.__dict__.update(
                    self.__class__.objects.filter(id=self.id).values(*put_back)[0]
                )
                for f in put_back:
                    denorm_update.send(sender=self.__class__, instance=self, field=f,
                                       old=self._original_state[f], new=self.__dict__[f])
            except:
                #todo: log this properly
                pass

        self._original_state = dict(self.__dict__)
        self.__class__.objects.cache_obj(self)

    def delete(self):
        cache.delete(self.cache_key(self.pk))
        super(BaseModel, self).delete()


class ActiveObjectManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return super(ActiveObjectManager, self).get_query_set().filter(canceled=False)

class UndeletedObjectManager(models.Manager):
    def get_query_set(self):
        return super(UndeletedObjectManager, self).get_query_set().filter(deleted=False)

class GenericContent(models.Model):
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        app_label = 'forum'

class MetaContent(BaseModel):
    node = models.ForeignKey('Node', null=True, related_name='%(class)ss')

    def __init__(self, *args, **kwargs):
        if 'content_object' in kwargs:
            kwargs['node'] = kwargs['content_object']
            del kwargs['content_object']

        super (MetaContent, self).__init__(*args, **kwargs)
    
    @property
    def content_object(self):
        return self.node.leaf

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

mark_canceled = django.dispatch.Signal(providing_args=['instance'])

class CancelableContent(models.Model):
    canceled = models.BooleanField(default=False)

    def cancel(self):
        if not self.canceled:
            self.canceled = True
            self.save()
            mark_canceled.send(sender=self.__class__, instance=self)
            return True
            
        return False

    class Meta:
        abstract = True
        app_label = 'forum'


from node import Node, NodeRevision

class QandA(Node):
    wiki                 = models.BooleanField(default=False)
    wikified_at          = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'forum'

    def wikify(self):
        if not self.wiki:
            self.wiki = True
            self.wikified_at = datetime.datetime.now()
            self.save()




