from django import template

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
