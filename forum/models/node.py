from base import *
from tag import Tag

import markdown
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from forum.utils.html import sanitize_html

class NodeContent(models.Model):
    title      = models.CharField(max_length=300)
    tagnames   = models.CharField(max_length=125)
    author     = models.ForeignKey(User, related_name='%(class)ss')
    body       = models.TextField()

    @property
    def user(self):
        return self.author

    @property
    def html(self):
        return mark_safe(sanitize_html(markdown.markdown(self.body)))

    @property
    def headline(self):
        return self.title

    def tagname_list(self):
        if self.tagnames:
            return [name for name in self.tagnames.split(u' ')]
        else:
            return []

    def tagname_meta_generator(self):
        return u','.join([unicode(tag) for tag in self.tagname_list()])

    class Meta:
        abstract = True
        app_label = 'forum'

class NodeMetaClass(models.Model.__metaclass__):
    types = {}

    def __new__(cls, *args, **kwargs):
        new_cls = super(NodeMetaClass, cls).__new__(cls, *args, **kwargs)

        if not new_cls._meta.abstract and new_cls.__name__ is not 'Node':
            NodeMetaClass.types[new_cls.__name__.lower()] = new_cls

        return new_cls

    @classmethod
    def setup_relations(cls):
        for node_cls in NodeMetaClass.types.values():
            NodeMetaClass.setup_relation(node_cls)        

    @classmethod
    def setup_relation(cls, node_cls):
        name = node_cls.__name__.lower()

        def children(self):
            if node_cls._meta.proxy:
                return node_cls.objects.filter(node_type=name, parent=self)
            else:
                return node_cls.objects.filter(parent=self)

        def parent(self):
            p = self.__dict__.get('_%s_cache' % name, None)

            if p is None and (self.parent is not None) and self.parent.node_type == name:
                p = self.parent.leaf
                self.__dict__['_%s_cache' % name] = p

            return p

        Node.add_to_class(name + 's', property(children))
        Node.add_to_class(name, property(parent))


node_create = django.dispatch.Signal(providing_args=['instance'])

class Node(BaseModel, NodeContent, DeletableContent):
    __metaclass__ = NodeMetaClass

    node_type            = models.CharField(max_length=16, default='node')
    parent               = models.ForeignKey('Node', related_name='children', null=True)
    abs_parent           = models.ForeignKey('Node', related_name='all_children', null=True)

    added_at             = models.DateTimeField(default=datetime.datetime.now)

    tags                 = models.ManyToManyField('Tag', related_name='%(class)ss')

    score                 = models.IntegerField(default=0)
    vote_up_count         = models.IntegerField(default=0)
    vote_down_count       = models.IntegerField(default=0)

    comment_count         = models.PositiveIntegerField(default=0)
    offensive_flag_count  = models.SmallIntegerField(default=0)

    last_edited_at        = models.DateTimeField(null=True, blank=True)
    last_edited_by        = models.ForeignKey(User, null=True, blank=True, related_name='last_edited_%(class)ss')

    active_revision       = models.OneToOneField('NodeRevision', related_name='active', null=True)

    @property
    def leaf(self):
        return NodeMetaClass.types[self.node_type].objects.get(id=self.id)

    @property    
    def absolute_parent(self):
        if not self.abs_parent_id:
            return self.leaf

        return self.abs_parent.leaf

    @property
    def summary(self):
        return strip_tags(self.html)[:300]

    def create_revision(self, user, **kwargs):
        revision = NodeRevision(author=user, **kwargs)
        
        if not self.id:
            self.author = user
            self.save()
            revision.revision = 1
        else:
            revision.revision = self.revisions.aggregate(last=models.Max('revision'))['last'] + 1

        revision.node_id = self.id
        revision.save()
        self.activate_revision(user, revision)

    def activate_revision(self, user, revision):
        self.title = revision.title
        self.tagnames = revision.tagnames
        self.body = revision.body

        old_revision = self.active_revision

        self.active_revision = revision
        self.save()

        if not old_revision:
            self.last_edited_at = datetime.datetime.now()
            self.last_edited_by = user
            node_create.send(sender=self.__class__, instance=self)

    def get_tag_list_if_changed(self):
        dirty = self.get_dirty_fields()

        if 'tagnames' in dirty:
            new_tags = self.tagname_list()
            old_tags = dirty['tagnames']

            if old_tags is None or not old_tags:
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
        if not self.id:
            self.node_type = self.__class__.__name__.lower()

        if self.parent_id and not self.abs_parent_id:
            self.abs_parent = self.parent.absolute_parent

        self.__dict__['score'] = self.__dict__['vote_up_count'] - self.__dict__['vote_down_count']
            
        tags = self.get_tag_list_if_changed()
        super(Node, self).save(*args, **kwargs)
        if tags is not None: self.tags = tags

    class Meta:
        app_label = 'forum'


class NodeRevision(NodeContent):
    node       = models.ForeignKey(Node, related_name='revisions')
    summary    = models.CharField(max_length=300)
    revision   = models.PositiveIntegerField()
    revised_at = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = ('node', 'revision')
        app_label = 'forum'


from user import ValidationHash

class AnonymousNode(Node):
    validation_hash = models.ForeignKey(Node, related_name='anonymous_content')
    convertible_to = models.CharField(max_length=16, default='node')

    class Meta:
        app_label = 'forum'