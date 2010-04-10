from django import template
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from forum.models import Tag, MarkedTag

register = template.Library()

@register.inclusion_tag('question_list/item.html')
def question_list_item(question):
    return {'question': question}

@register.inclusion_tag('question_list/sort_tabs.html')
def question_sort_tabs(sort_context):
    return sort_context

@register.inclusion_tag('question_list/related_tags.html')
def question_list_related_tags(questions):
    if len(questions):
        return {'tags': Tag.objects.filter(questions__id__in=[q.id for q in questions]).distinct()}
    else:
        return {'tags': False}

@register.inclusion_tag('question_list/tag_selector.html', takes_context=True)
def tag_selector(context):
    request = context['request']

    if request.user.is_authenticated():
        pt = MarkedTag.objects.filter(user=request.user)
        return {
            "interesting_tag_names": pt.filter(reason='good').values_list('tag__name', flat=True),
            'ignored_tag_names': pt.filter(reason='bad').values_list('tag__name', flat=True),
            'user_authenticated': True,
        }
    else:
        return {'user_authenticated': False}

@register.inclusion_tag('question_list/count.html', takes_context=True)
def question_list_count(context):
    context['sort_description'] = mark_safe({
        'latest': _('<strong>Newest</strong> questions are shown first. '),
        'active': _('Questions are sorted by the <strong>time of last update</strong>.'),
        'hottest': _('Questions sorted by <strong>number of responses</strong>.'),
        'mostvoted': _('Questions are sorted by the <strong>number of votes</strong>.')
    }.get(context['request'].utils.sort_method('latest'), ''))

    return context

@register.inclusion_tag('question_list/title.html', takes_context=True)
def question_list_title(context):
    return context