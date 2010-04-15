import re
from datetime import date
from django import forms
from models import *
from const import *
from django.utils.translation import ugettext as _
from forum.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from forum.utils.forms import NextUrlField, UserNameField, SetPasswordForm
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import logging

class TitleField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(TitleField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.TextInput(attrs={'size' : 70, 'autocomplete' : 'off'})
        self.max_length = 255
        self.label  = _('title')
        self.help_text = _('please enter a descriptive title for your question')
        self.initial = ''

    def clean(self, value):
        if len(value) < 10:
            raise forms.ValidationError(_('title must be > 10 characters'))

        return value

class EditorField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(EditorField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.Textarea(attrs={'id':'editor'})
        self.label  = _('content')
        self.help_text = u''
        self.initial = ''

    def clean(self, value):
        if len(value) < 10:
            raise forms.ValidationError(_('question content must be > 10 characters'))

        return value

class TagNamesField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(TagNamesField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'})
        self.max_length = 255
        self.label  = _('tags')
        #self.help_text = _('please use space to separate tags (this enables autocomplete feature)')
        self.help_text = _('Tags are short keywords, with no spaces within. Up to five tags can be used.')
        self.initial = ''

    def clean(self, value):
        value = super(TagNamesField, self).clean(value)
        data = value.strip()
        if len(data) < 1:
            raise forms.ValidationError(_('tags are required'))

        split_re = re.compile(r'[ ,]+')
        list = split_re.split(data)
        list_temp = []
        if len(list) > 5:
            raise forms.ValidationError(_('please use 5 tags or less'))

        tagname_re = re.compile(r'[a-z0-9]+')
        for tag in list:
            if len(tag) > 20:
                raise forms.ValidationError(_('tags must be shorter than 20 characters'))
            if not tagname_re.match(tag):
                raise forms.ValidationError(_('please use following characters in tags: letters \'a-z\', numbers, and characters \'.-_#\''))
            # only keep one same tag
            if tag not in list_temp and len(tag.strip()) > 0:
                list_temp.append(tag)
        return u' '.join(list_temp)

class WikiField(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        super(WikiField, self).__init__(*args, **kwargs)
        self.required = False
        self.label  = _('community wiki')
        self.help_text = _('if you choose community wiki option, the question and answer do not generate points and name of author will not be shown')
    def clean(self,value):
        return value and settings.WIKI_ON

class EmailNotifyField(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        super(EmailNotifyField, self).__init__(*args, **kwargs)
        self.required = False
        self.widget.attrs['class'] = 'nomargin'

class SummaryField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(SummaryField, self).__init__(*args, **kwargs)
        self.required = False
        self.widget = forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'})
        self.max_length = 300
        self.label  = _('update summary:')
        self.help_text = _('enter a brief summary of your revision (e.g. fixed spelling, grammar, improved style, this field is optional)')

class ModerateUserForm(forms.ModelForm):
    is_approved = forms.BooleanField(label=_("Automatically accept user's contributions for the email updates"),
                                     required=False)

    def clean_is_approved(self):
        if 'is_approved' not in self.cleaned_data:
            self.cleaned_data['is_approved'] = False
        return self.cleaned_data['is_approved']

    class Meta:
        model = User
        fields = ('is_approved',)

class FeedbackForm(forms.Form):
    name = forms.CharField(label=_('Your name:'), required=False)
    email = forms.EmailField(label=_('Email (not shared with anyone):'), required=False)
    message = forms.CharField(label=_('Your message:'), max_length=800,widget=forms.Textarea(attrs={'cols':60}))
    next = NextUrlField()

class AskForm(forms.Form):
    title  = TitleField()
    text   = EditorField()
    tags   = TagNamesField()
    wiki = WikiField()


class AnswerForm(forms.Form):
    text   = EditorField()
    wiki   = WikiField()

    def __init__(self, question, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)

        if question.wiki and settings.WIKI_ON:
            self.fields['wiki'].initial = True


class CloseForm(forms.Form):
    reason = forms.ChoiceField(choices=CLOSE_REASONS)

class RetagQuestionForm(forms.Form):
    tags   = TagNamesField()
    # initialize the default values
    def __init__(self, question, *args, **kwargs):
        super(RetagQuestionForm, self).__init__(*args, **kwargs)
        self.fields['tags'].initial = question.tagnames

class RevisionForm(forms.Form):
    """
    Lists revisions of a Question or Answer
    """
    revision = forms.ChoiceField(widget=forms.Select(attrs={'style' : 'width:520px'}))

    def __init__(self, post, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)

        revisions = post.revisions.all().values_list(
            'revision', 'author__username', 'revised_at', 'summary')
        date_format = '%c'
        self.fields['revision'].choices = [
            (r[0], u'%s - %s (%s) %s' % (r[0], r[1], r[2].strftime(date_format), r[3]))
            for r in revisions]

        self.fields['revision'].initial = post.active_revision.revision

class EditQuestionForm(forms.Form):
    title  = TitleField()
    text   = EditorField()
    tags   = TagNamesField()
    summary = SummaryField()

    def __init__(self, question, revision=None, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)

        if revision is None:
            revision = question.active_revision

        self.fields['title'].initial = revision.title
        self.fields['text'].initial = revision.body
        self.fields['tags'].initial = revision.tagnames
            
        # Once wiki mode is enabled, it can't be disabled
        if not question.wiki:
            self.fields['wiki'] = WikiField()

class EditAnswerForm(forms.Form):
    text = EditorField()
    summary = SummaryField()

    def __init__(self, answer, revision=None, *args, **kwargs):
        super(EditAnswerForm, self).__init__(*args, **kwargs)

        if revision is None:
            revision = answer.active_revision

        self.fields['text'].initial = revision.body

class EditUserForm(forms.Form):
    email = forms.EmailField(label=u'Email', help_text=_('this email does not have to be linked to gravatar'), required=True, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    if settings.EDITABLE_SCREEN_NAME:
    	username = UserNameField(label=_('Screen name'))
    realname = forms.CharField(label=_('Real name'), required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    website = forms.URLField(label=_('Website'), required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    city = forms.CharField(label=_('Location'), required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    birthday = forms.DateField(label=_('Date of birth'), help_text=_('will not be shown, used to calculate age, format: YYYY-MM-DD'), required=False, widget=forms.TextInput(attrs={'size' : 35}))
    about = forms.CharField(label=_('Profile'), required=False, widget=forms.Textarea(attrs={'cols' : 60}))

    def __init__(self, user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        logging.debug('initializing the form')
        if settings.EDITABLE_SCREEN_NAME:
            self.fields['username'].initial = user.username
            self.fields['username'].user_instance = user
        self.fields['email'].initial = user.email
        self.fields['realname'].initial = user.real_name
        self.fields['website'].initial = user.website
        self.fields['city'].initial = user.location

        if user.date_of_birth is not None:
            self.fields['birthday'].initial = user.date_of_birth
        else:
            self.fields['birthday'].initial = '1990-01-01'
        self.fields['about'].initial = user.about
        self.user = user

    def clean_email(self):
        """For security reason one unique email in database"""
        if self.user.email != self.cleaned_data['email']:
            #todo dry it, there is a similar thing in openidauth
            if settings.EMAIL_UNIQUE == True:
                if 'email' in self.cleaned_data:
                    try:
                        user = User.objects.get(email = self.cleaned_data['email'])
                    except User.DoesNotExist:
                        return self.cleaned_data['email']
                    except User.MultipleObjectsReturned:
                        raise forms.ValidationError(_('this email has already been registered, please use another one'))
                    raise forms.ValidationError(_('this email has already been registered, please use another one'))
        return self.cleaned_data['email']


class SubscriptionSettingsForm(forms.Form):
    member_joins = forms.ChoiceField(widget=forms.RadioSelect, choices=NOTIFICATION_CHOICES)
    new_question = forms.ChoiceField(widget=forms.RadioSelect, choices=NOTIFICATION_CHOICES)
    new_question_watched_tags = forms.ChoiceField(widget=forms.RadioSelect, choices=NOTIFICATION_CHOICES)
    subscribed_questions = forms.ChoiceField(widget=forms.RadioSelect, choices=NOTIFICATION_CHOICES)

    all_questions = forms.BooleanField(required=False, initial=False)
    all_questions_watched_tags = forms.BooleanField(required=False, initial=False)
    questions_asked = forms.BooleanField(required=False, initial=False)
    questions_answered = forms.BooleanField(required=False, initial=False)
    questions_commented = forms.BooleanField(required=False, initial=False)
    questions_viewed = forms.BooleanField(required=False, initial=False)

    notify_answers = forms.BooleanField(required=False, initial=False)
    notify_reply_to_comments = forms.BooleanField(required=False, initial=False)
    notify_comments_own_post = forms.BooleanField(required=False, initial=False)
    notify_comments = forms.BooleanField(required=False, initial=False)
    notify_accepted = forms.BooleanField(required=False, initial=False)

