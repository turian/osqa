from django import template
from django.utils.translation import ugettext as _
from forum import const

register = template.Library()

class UserSignatureNode(template.Node):
    template = template.loader.get_template('users/signature.html')

    def __init__(self, user, format):
        self.user = template.Variable(user)
        self.format = template.Variable(format)

    def render(self, context):
        return self.template.render(template.Context({
            'user': self.user.resolve(context),
            'format': self.format.resolve(context)
        }))

@register.tag        
def user_signature(parser, token):
    try:
        tag_name, user, format = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]

    return UserSignatureNode(user, format)


class ActivityNode(template.Node):
    template = template.loader.get_template('users/activity.html')

    def __init__(self, activity):
        self.activity = template.Variable(activity)

    def render(self, context):
        try:
            activity = self.activity.resolve(context)

            context = {
                'active_at': activity.active_at,
                'description': activity.type_as_string,
                'type': activity.activity_type,
            }

            if activity.activity_type == const.TYPE_ACTIVITY_PRIZE:
                context['badge'] = True
                context['title'] = activity.content_object.badge.name
                context['url'] = activity.content_object.badge.get_absolute_url()
                context['badge_type'] = activity.content_object.badge.type
            else:
                context['title'] = activity.node.headline
                context['url'] = activity.node.get_absolute_url()

            if activity.activity_type in (const.TYPE_ACTIVITY_UPDATE_ANSWER, const.TYPE_ACTIVITY_UPDATE_QUESTION):
                context['revision'] = True
                context['summary'] = activity.content_object.summary or \
                        _('Revision n. %(rev_number)d') % {'rev_number': activity.content_object.revision}

            return self.template.render(template.Context(context))
        except Exception, e:
            return ''

@register.tag
def activity_item(parser, token):
    try:
        tag_name, activity = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]

    return ActivityNode(activity)
