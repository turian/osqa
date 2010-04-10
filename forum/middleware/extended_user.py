from django.contrib.auth.middleware import AuthenticationMiddleware
from forum.models.user import AnonymousUser

class ExtendedUser(AuthenticationMiddleware):    
    def process_request(self, request):
        super(ExtendedUser, self).process_request(request)
        if request.user.is_authenticated():
            try:
                request.user = request.user.user
                return None
            except:
                pass

        request.user = AnonymousUser()
        return None