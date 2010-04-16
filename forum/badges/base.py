import re
from string import lower

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from forum.models.user import activity_record
from forum.models import Badge, Award, Activity, Node

import logging

class AbstractBadge(object):

    _instance = None

    @property
    def name(self):
        return " ".join(re.findall(r'([A-Z][a-z1-9]+)', re.sub('Badge', '', self.__class__.__name__)))

    @property
    def description(self):
        raise NotImplementedError

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls.badge = "-".join(map(lower, re.findall(r'([A-Z][a-z1-9]+)', re.sub('Badge', '', cls.__name__)))) 
            cls._instance = super(AbstractBadge, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def install(self):
        try:
            installed = Badge.objects.get(slug=self.badge)
        except:
            badge = Badge(name=self.name, description=self.description, slug=self.badge, type=self.type)
            badge.save()

    def award_badge(self, user, obj=None, award_once=False):
        try:
            badge = Badge.objects.get(slug=self.badge)
        except:
            logging.log('Trying to award a badge not installed in the database.')
            return
            
        content_type = ContentType.objects.get_for_model(obj.__class__)

        awarded = user.awards.filter(badge=badge)

        if not award_once:
            awarded = awarded.filter(content_type=content_type, object_id=obj.id)

        if len(awarded):
            logging.log(1, 'Trying to award badged already awarded.')
            return
            
        award = Award(user=user, badge=badge, content_type=content_type, object_id=obj.id)
        award.save()

class CountableAbstractBadge(AbstractBadge):

    def __init__(self, model, field, expected_value, handler):
        def wrapper(instance, **kwargs):
            dirty_fields = instance.get_dirty_fields()
            if field in dirty_fields and instance.__dict__[field] == expected_value:
                handler(instance=instance)
        
        post_save.connect(wrapper, sender=model, weak=False)

class PostCountableAbstractBadge(CountableAbstractBadge):
    def __init__(self, model, field, expected_value):

        def handler(instance):            
            self.award_badge(instance.author, instance)

        super(PostCountableAbstractBadge, self).__init__(model, field, expected_value, handler)

class NodeCountableAbstractBadge(CountableAbstractBadge):
    def __init__(self, node_type, field, expected_value):

        def handler(instance):
            if instance.node_type == node_type:
                self.award_badge(instance.author, instance)

        super(NodeCountableAbstractBadge, self).__init__(Node, field, expected_value, handler)

class ActivityAbstractBadge(AbstractBadge):

    def __init__(self, activity_type, handler):

        def wrapper(sender, **kwargs):
            handler(instance=kwargs['instance'])

        activity_record.connect(wrapper, sender=activity_type, weak=False)


class ActivityCountAbstractBadge(AbstractBadge):

    def __init__(self, activity_type, count):

        def handler(sender, **kwargs):
            instance = kwargs['instance']
            if Activity.objects.filter(user=instance.user, activity_type__in=activity_type).count() == count:
                self.award_badge(instance.user, instance.content_object)

        if not isinstance(activity_type, (tuple, list)):
            activity_type = (activity_type, )

        for type in activity_type:
            activity_record.connect(handler, sender=type, weak=False)

class FirstActivityAbstractBadge(ActivityCountAbstractBadge):

    def __init__(self, activity_type):
        super(FirstActivityAbstractBadge, self).__init__(activity_type, 1)
