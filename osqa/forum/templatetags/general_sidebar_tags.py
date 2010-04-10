from django import template
from forum.models import Tag, Award

#todo: move to settings
RECENT_TAGS_SIZE = 25
RECENT_AWARD_SIZE = 15

register = template.Library()

@register.inclusion_tag('sidebar/recent_tags.html')
def recent_tags():
    return {'tags': Tag.active.order_by('-id')[:RECENT_TAGS_SIZE]}

@register.inclusion_tag('sidebar/recent_awards.html')
def recent_awards():
    return {'awards': Award.objects.get_recent_awards()[:RECENT_AWARD_SIZE]}