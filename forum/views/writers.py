# encoding:utf-8
import os.path
import time, datetime, random
import logging
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.utils.html import *
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from forum.utils.html import sanitize_html
from markdown2 import Markdown
from forum.forms import *
from forum.models import *
from forum.const import *
from forum.utils.forms import get_next_url
from forum.views.readers import _get_tags_cache_json

# used in index page
INDEX_PAGE_SIZE = 20
INDEX_AWARD_SIZE = 15
INDEX_TAGS_SIZE = 100
# used in tags list
DEFAULT_PAGE_SIZE = 60
# used in questions
QUESTIONS_PAGE_SIZE = 10
# used in answers
ANSWERS_PAGE_SIZE = 10

markdowner = Markdown(html4tags=True)

def upload(request):#ajax upload file to a question or answer
    class FileTypeNotAllow(Exception):
        pass
    class FileSizeNotAllow(Exception):
        pass
    class UploadPermissionNotAuthorized(Exception):
        pass

    #<result><msg><![CDATA[%s]]></msg><error><![CDATA[%s]]></error><file_url>%s</file_url></result>
    xml_template = "<result><msg><![CDATA[%s]]></msg><error><![CDATA[%s]]></error><file_url>%s</file_url></result>"

    try:
        f = request.FILES['file-upload']
        # check upload permission
        if not request.user.can_upload_files():
            raise UploadPermissionNotAuthorized()

        # check file type
        file_name_suffix = os.path.splitext(f.name)[1].lower()

        if not file_name_suffix in ('.jpg', '.jpeg', '.gif', '.png', '.bmp', '.tiff', '.ico'):
            raise FileTypeNotAllow()

        storage = FileSystemStorage(str(settings.UPFILES_FOLDER), str(settings.UPFILES_ALIAS))
        new_file_name = storage.save(f.name, f)
        # check file size
        # byte
        size = storage.size(new_file_name)

        if size > float(settings.ALLOW_MAX_FILE_SIZE) * 1024 * 1024:
            storage.delete(new_file_name)
            raise FileSizeNotAllow()

        result = xml_template % ('Good', '', str(settings.UPFILES_ALIAS) + new_file_name)
    except UploadPermissionNotAuthorized:
        result = xml_template % ('', _('uploading images is limited to users with >60 reputation points'), '')
    except FileTypeNotAllow:
        result = xml_template % ('', _("allowed file types are 'jpg', 'jpeg', 'gif', 'bmp', 'png', 'tiff'"), '')
    except FileSizeNotAllow:
        result = xml_template % ('', _("maximum upload file size is %sM") % settings.ALLOW_MAX_FILE_SIZE, '')
    except Exception, e:
        result = xml_template % ('', _('Error uploading file. Please contact the site administrator. Thank you. %s' % e), '')

    return HttpResponse(result, mimetype="application/xml")


def ask(request):
    if request.method == "POST" and "text" in request.POST:
        form = AskForm(request.POST)
        if form.is_valid():

            added_at = datetime.datetime.now()
            title = strip_tags(form.cleaned_data['title'].strip())
            wiki = form.cleaned_data['wiki']
            tagnames = form.cleaned_data['tags'].strip()
            text = form.cleaned_data['text']
            html = sanitize_html(markdowner.convert(text))
            summary = strip_tags(html)[:120]
            
            if request.user.is_authenticated():
                author = request.user 

                question = Question.objects.create_new(
                    title            = title,
                    author           = author, 
                    added_at         = added_at,
                    wiki             = wiki,
                    tagnames         = tagnames,
                    summary          = summary,
                    text = sanitize_html(markdowner.convert(text))
                )

                return HttpResponseRedirect(question.get_absolute_url())
            else:
                request.session.flush()
                session_key = request.session.session_key
                question = AnonymousQuestion(
                    session_key = session_key,
                    title       = title,
                    tagnames = tagnames,
                    wiki = wiki,
                    text = text,
                    summary = summary,
                    added_at = added_at,
                    ip_addr = request.META['REMOTE_ADDR'],
                )
                question.save()
                return HttpResponseRedirect(reverse('auth_action_signin', kwargs={'action': 'newquestion'}))
    elif request.method == "POST" and "go" in request.POST:
        form = AskForm({'title': request.POST['q']})
    else:
        form = AskForm()

    tags = _get_tags_cache_json()
    return render_to_response('ask.html', {
        'form' : form,
        'tags' : tags,
        'email_validation_faq_url':reverse('faq') + '#validate',
        }, context_instance=RequestContext(request))

@login_required
def edit_question(request, id):#edit or retag a question
    """view to edit question
    """
    question = get_object_or_404(Question, id=id)
    if question.deleted and not request.user.can_view_deleted_post(question):
        raise Http404
    if request.user.can_edit_post(question):
        return _edit_question(request, question)
    elif request.user.can_retag_questions():
        return _retag_question(request, question)
    else:
        raise Http404

def _retag_question(request, question):#non-url subview of edit question - just retag
    """retag question sub-view used by
    view "edit_question"
    """
    if request.method == 'POST':
        form = RetagQuestionForm(question, request.POST)
        if form.is_valid():
            if form.has_changed():
                latest_revision = question.get_latest_revision()
                retagged_at = datetime.datetime.now()

                question.tagnames = form.cleaned_data['tags']
                question.last_edited_at = retagged_at
                question.last_edited_by = request.user
                question.last_activity_at = retagged_at
                question.last_activity_by = request.user
                question.save()

                # Create a new revision
                QuestionRevision.objects.create(
                    question   = question,
                    title      = latest_revision.title,
                    author     = request.user,
                    revised_at = retagged_at,
                    tagnames   = form.cleaned_data['tags'],
                    summary    = CONST['retagged'],
                    text       = latest_revision.text
                )

            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = RetagQuestionForm(question)
    return render_to_response('question_retag.html', {
        'question': question,
        'form' : form,
        'tags' : _get_tags_cache_json(),
    }, context_instance=RequestContext(request))

def _edit_question(request, question):#non-url subview of edit_question - just edit the body/title
    latest_revision = question.get_latest_revision()
    revision_form = None
    if request.method == 'POST':
        if 'select_revision' in request.POST:
            # user has changed revistion number
            revision_form = RevisionForm(question, latest_revision, request.POST)
            if revision_form.is_valid():
                # Replace with those from the selected revision
                form = EditQuestionForm(question,
                    QuestionRevision.objects.get(question=question,
                        revision=revision_form.cleaned_data['revision']))
            else:
                form = EditQuestionForm(question, latest_revision, request.POST)
        else:
            # Always check modifications against the latest revision
            form = EditQuestionForm(question, latest_revision, request.POST)
            if form.is_valid():
                html = sanitize_html(markdowner.convert(form.cleaned_data['text']))
                if form.has_changed():
                    edited_at = datetime.datetime.now()
                    tags_changed = (latest_revision.tagnames !=
                                    form.cleaned_data['tags'])

                    # Update the Question itself
                    question.title = form.cleaned_data['title']
                    question.last_edited_at = edited_at
                    question.last_edited_by = request.user
                    question.last_activity_at = edited_at
                    question.last_activity_by = request.user
                    question.tagnames = form.cleaned_data['tags']
                    question.summary = strip_tags(html)[:120]
                    question.html = html

                    # only save when it's checked
                    # because wiki doesn't allow to be edited if last version has been enabled already
                    # and we make sure this in forms.
                    if ('wiki' in form.cleaned_data and
                        form.cleaned_data['wiki']):
                        question.wiki = True
                        question.wikified_at = edited_at

                    question.save()

                    # Create a new revision
                    revision = QuestionRevision(
                        question   = question,
                        title      = form.cleaned_data['title'],
                        author     = request.user,
                        revised_at = edited_at,
                        tagnames   = form.cleaned_data['tags'],
                        text       = form.cleaned_data['text'],
                    )
                    if form.cleaned_data['summary']:
                        revision.summary = form.cleaned_data['summary']
                    else:
                        revision.summary = 'No.%s Revision' % latest_revision.revision
                    revision.save()

                return HttpResponseRedirect(question.get_absolute_url())
    else:

        revision_form = RevisionForm(question, latest_revision)
        form = EditQuestionForm(question, latest_revision)
    return render_to_response('question_edit.html', {
        'question': question,
        'revision_form': revision_form,
        'form' : form,
        'tags' : _get_tags_cache_json()
    }, context_instance=RequestContext(request))

@login_required
def edit_answer(request, id):
    answer = get_object_or_404(Answer, id=id)
    if answer.deleted and not request.user.can_view_deleted_post(answer):
        raise Http404
    elif not request.user.can_edit_post(answer):
        raise Http404
    else:
        latest_revision = answer.get_latest_revision()
        if request.method == "POST":
            if 'select_revision' in request.POST:
                # user has changed revistion number
                revision_form = RevisionForm(answer, latest_revision, request.POST)
                if revision_form.is_valid():
                    # Replace with those from the selected revision
                    form = EditAnswerForm(answer,
                                          AnswerRevision.objects.get(answer=answer,
                                          revision=revision_form.cleaned_data['revision']))
                else:
                    form = EditAnswerForm(answer, latest_revision, request.POST)
            else:
                form = EditAnswerForm(answer, latest_revision, request.POST)
                if form.is_valid():
                    html = sanitize_html(markdowner.convert(form.cleaned_data['text']))
                    if form.has_changed():
                        edited_at = datetime.datetime.now()
                        updated_fields = {
                            'last_edited_at': edited_at,
                            'last_edited_by': request.user,
                            'html': html,
                        }
                        Answer.objects.filter(id=answer.id).update(**updated_fields)

                        revision = AnswerRevision(
                                                  answer=answer,
                                                  author=request.user,
                                                  revised_at=edited_at,
                                                  text=form.cleaned_data['text']
                                                  )

                        if form.cleaned_data['summary']:
                            revision.summary = form.cleaned_data['summary']
                        else:
                            revision.summary = 'No.%s Revision' % latest_revision.revision
                        revision.save()

                        answer.question.last_activity_at = edited_at
                        answer.question.last_activity_by = request.user
                        answer.question.save()

                    return HttpResponseRedirect(answer.get_absolute_url())
        else:
            revision_form = RevisionForm(answer, latest_revision)
            form = EditAnswerForm(answer, latest_revision)
        return render_to_response('answer_edit.html', {
                                  'answer': answer,
                                  'revision_form': revision_form,
                                  'form': form,
                                  }, context_instance=RequestContext(request))

def answer(request, id):#process a new answer
    question = get_object_or_404(Question, id=id)
    if request.method == "POST":
        form = AnswerForm(question, request.user, request.POST)
        if form.is_valid():
            wiki = form.cleaned_data['wiki']
            text = form.cleaned_data['text']
            update_time = datetime.datetime.now()

            if request.user.is_authenticated():
                Answer.objects.create_new(
                                  question=question,
                                  author=request.user,
                                  added_at=update_time,
                                  wiki=wiki,
                                  text=sanitize_html(markdowner.convert(text)),
                                  email_notify=form.cleaned_data['email_notify']
                                  )
            else:
                request.session.flush()
                html = sanitize_html(markdowner.convert(text))
                summary = strip_tags(html)[:120]
                anon = AnonymousAnswer(
                                       question=question,
                                       wiki=wiki,
                                       text=text,
                                       summary=summary,
                                       session_key=request.session.session_key,
                                       ip_addr=request.META['REMOTE_ADDR'],
                                       )
                anon.save()
                return HttpResponseRedirect(reverse('auth_action_signin', kwargs={'action': 'newanswer'}))

    return HttpResponseRedirect(question.get_absolute_url())

