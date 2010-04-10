from forum.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from forms import ClassicRegisterForm
from forum.authentication.forms import SimpleEmailSubscribeForm
from forum.views.auth import login_and_forward, send_validation_email

def register(request):
    if request.method == 'POST':
        form = ClassicRegisterForm(request.POST)
        email_feeds_form = SimpleEmailSubscribeForm(request.POST)

        if form.is_valid() and email_feeds_form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']

            user_ = User(username=username, email=email)
            user_.set_password(password)

            if User.objects.all().count() == 0:
                user_.is_superuser = True

            user_.save()
            
            send_validation_email(user_)
            if email_feeds_form.cleaned_data['subscribe'] == 'n':
                user_.subscription_settings.enable_notifications = False
                user_.subscription_settings.save()

            return login_and_forward(request, user_, None, _("A validation email has been sent to your email address. "))
    else:
        form = ClassicRegisterForm(initial={'next':'/'})
        email_feeds_form = SimpleEmailSubscribeForm()

    return render_to_response('auth/signup.html', {
        'form': form,
        'email_feeds_form': email_feeds_form
        }, context_instance=RequestContext(request))