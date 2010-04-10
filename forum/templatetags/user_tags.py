from django import template

register = template.Library()


@register.inclusion_tag('users/info_small_lite.html')
def user_signature_small_lite(user):
    return {
        'name': user.username,
        'url': user.get_absolute_url(),
        'reputation': user.reputation,
    }

@register.inclusion_tag('users/info_small_full.html')
def user_signature_small_full(user):
    return {
        'name': user.username,
        'url': user.get_absolute_url(),
        'reputation': user.reputation,
        'bronze': user.bronze,
        'silver': user.silver,
        'gold': user.gold
    }
    pass