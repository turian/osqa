# encoding:utf-8
import datetime
import logging
from urllib import unquote
from django.conf import settings as django_settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404, HttpResponsePermanentRedirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from django import template
from django.utils.html import *
from django.utils import simplejson
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.views.decorators.cache import cache_page
from django.utils.http import urlquote  as django_urlquote
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from forum.utils.html import sanitize_html
from forum.utils.diff import textDiff as htmldiff
from forum.forms import *
from forum.models import *
from forum.const import *
from forum.utils.forms import get_next_url
from forum.models.question import question_view
import decorators

# used in index page
#refactor - move these numbers somewhere?
INDEX_PAGE_SIZE = 30
INDEX_AWARD_SIZE = 15
INDEX_TAGS_SIZE = 25
# used in tags list
DEFAULT_PAGE_SIZE = 60
# used in questions
QUESTIONS_PAGE_SIZE = 30
# used in answers
ANSWERS_PAGE_SIZE = 10

#system to display main content
def _get_tags_cache_json():#service routine used by views requiring tag list in the javascript space
    """returns list of all tags in json format
    no caching yet, actually
    """
    tags = Tag.objects.filter(deleted=False).all()
    tags_list = []
    for tag in tags:
        dic = {'n': tag.name, 'c': tag.used_count}
        tags_list.append(dic)
    tags = simplejson.dumps(tags_list)
    return tags

@decorators.render('index.html')
def index(request):
    return question_list(request, Question.objects.all(), sort='active', base_path=reverse('questions'))

@decorators.render('questions.html', 'unanswered')
def unanswered(request):
    return question_list(request, Question.objects.filter(accepted_answer=None),
                         _('Open questions without an accepted answer'))

@decorators.render('questions.html', 'questions')
def questions(request):
    return question_list(request, Question.objects.all())

@decorators.render('questions.html')
def tag(request, tag):
    return question_list(request, Question.objects.filter(tags__name=unquote(tag)),
                        mark_safe(_('Questions tagged <span class="tag">%(tag)s</span>') % {'tag': tag}))

@decorators.list('questions', QUESTIONS_PAGE_SIZE)
def question_list(request, initial, list_description=_('questions'), sort=None, base_path=None):
    pagesize = request.utils.page_size(QUESTIONS_PAGE_SIZE)
    page = int(request.GET.get('page', 1))

    questions = initial.filter(deleted=False)

    if request.user.is_authenticated():
        questions = questions.filter(
                ~Q(tags__id__in=request.user.marked_tags.filter(user_selections__reason='bad')))

    if sort is not False:
        if sort is None:
            sort = request.utils.sort_method('latest')
        else:
            request.utils.set_sort_method(sort)

        view_dic = {"latest":"-added_at", "active":"-last_activity_at", "hottest":"-answer_count", "mostvoted":"-score" }

        questions=questions.order_by(view_dic.get(sort, '-added_at'))

    return {
        "questions" : questions,
        "questions_count" : questions.count(),
        "tags_autocomplete" : _get_tags_cache_json(),
        "list_description": list_description,
        "base_path" : base_path,
        }


def search(request):
    if request.method == "GET" and "q" in request.GET:
        keywords = request.GET.get("q")
        search_type = request.GET.get("t")
        
        if not keywords:
            return HttpResponseRedirect(reverse(index))
        if search_type == 'tag':
            return HttpResponseRedirect(reverse('tags') + '?q=%s' % (keywords.strip()))
        elif search_type == "user":
            return HttpResponseRedirect(reverse('users') + '?q=%s' % (keywords.strip()))
        elif search_type == "question":
            return question_search(request, keywords)
    else:
        return render_to_response("search.html", context_instance=RequestContext(request))

@decorators.render('questions.html')
def question_search(request, keywords):
    def question_search(keywords):
        return Question.objects.filter(Q(title__icontains=keywords) | Q(body__icontains=keywords))

    from forum.modules import get_handler

    question_search = get_handler('question_search', question_search)
    initial = question_search(keywords)

    return question_list(request, initial, _("questions matching '%(keywords)s'") % {'keywords': keywords},
            base_path="%s?t=question&q=%s" % (reverse('search'), django_urlquote(keywords)), sort=False)
    

def tags(request):#view showing a listing of available tags - plain list
    stag = ""
    is_paginated = True
    sortby = request.GET.get('sort', 'used')
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    if request.method == "GET":
        stag = request.GET.get("q", "").strip()
        if stag != '':
            objects_list = Paginator(Tag.objects.filter(deleted=False).exclude(used_count=0).extra(where=['name like %s'], params=['%' + stag + '%']), DEFAULT_PAGE_SIZE)
        else:
            if sortby == "name":
                objects_list = Paginator(Tag.objects.all().filter(deleted=False).exclude(used_count=0).order_by("name"), DEFAULT_PAGE_SIZE)
            else:
                objects_list = Paginator(Tag.objects.all().filter(deleted=False).exclude(used_count=0).order_by("-used_count"), DEFAULT_PAGE_SIZE)

    try:
        tags = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        tags = objects_list.page(objects_list.num_pages)

    return render_to_response('tags.html', {
                                            "tags" : tags,
                                            "stag" : stag,
                                            "tab_id" : sortby,
                                            "keywords" : stag,
                                            "context" : {
                                                'is_paginated' : is_paginated,
                                                'pages': objects_list.num_pages,
                                                'page': page,
                                                'has_previous': tags.has_previous(),
                                                'has_next': tags.has_next(),
                                                'previous': tags.previous_page_number(),
                                                'next': tags.next_page_number(),
                                                'base_url' : reverse('tags') + '?sort=%s&' % sortby
                                            }
                                }, context_instance=RequestContext(request))

def get_answer_sort_order(request):
    view_dic = {"latest":"-added_at", "oldest":"added_at", "votes":"-score" }

    view_id = request.GET.get('sort', request.session.get('answer_sort_order', None))

    if view_id is None or not view_id in view_dic:
        view_id = "votes"

    if view_id != request.session.get('answer_sort_order', None):
        request.session['answer_sort_order'] = view_id

    return (view_id, view_dic[view_id])

def update_question_view_times(request, question):
    if not 'last_seen_in_question' in request.session:
        request.session['last_seen_in_question'] = {}

    last_seen = request.session['last_seen_in_question'].get(question.id,None)

    if (not last_seen) or last_seen < question.last_activity_at:
        question_view.send(sender=update_question_view_times, instance=question, user=request.user)
        request.session['last_seen_in_question'][question.id] = datetime.datetime.now()

    request.session['last_seen_in_question'][question.id] = datetime.datetime.now()

def match_question_slug(slug):
    slug_words = slug.split('-')
    qs = Question.objects.filter(title__istartswith=slug_words[0])

    for q in qs:
        if slug == urlquote(slugify(q.title)):
            return q

    return None

def question(request, id, slug):
    try:
        question = Question.objects.get(id=id)
    except:
        question = match_question_slug(slug)
        if question is not None:
            return HttpResponsePermanentRedirect(question.get_absolute_url())
        else:
            raise Http404()

    if slug != urlquote(slugify(question.title)):
        return HttpResponsePermanentRedirect(question.get_absolute_url())

    page = int(request.GET.get('page', 1))
    view_id, order_by = get_answer_sort_order(request)

    if question.deleted and not request.user.can_view_deleted_post(question):
        raise Http404

    answer_form = AnswerForm(question)
    answers = request.user.get_visible_answers(question)

    if answers is not None:
        answers = [a for a in answers.order_by("-accepted", order_by)
                   if not a.deleted or a.author == request.user]

    objects_list = Paginator(answers, ANSWERS_PAGE_SIZE)
    page_objects = objects_list.page(page)

    update_question_view_times(request, question)

    if request.user.is_authenticated():
        try:
            subscription = QuestionSubscription.objects.get(question=question, user=request.user)
        except:
            subscription = False
    else:
        subscription = False

    return render_to_response('question.html', {
        "question" : question,
        "answer" : answer_form,
        "answers" : page_objects.object_list,
        "tags" : question.tags.all(),
        "tab_id" : view_id,
        "similar_questions" : question.get_related_questions(),
        "subscription": subscription,
        "context" : {
            'is_paginated' : True,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': page_objects.has_previous(),
            'has_next': page_objects.has_next(),
            'previous': page_objects.previous_page_number(),
            'next': page_objects.next_page_number(),
            'base_url' : request.path + '?sort=%s&' % view_id,
            'extend_url' : "#sort-top"
        }
        }, context_instance=RequestContext(request))


REVISION_TEMPLATE = template.loader.get_template('node/revision.html')

def revisions(request, id):
    post = get_object_or_404(Node, id=id).leaf
    revisions = list(post.revisions.order_by('revised_at'))

    rev_ctx = []

    for i, revision in enumerate(revisions):
        rev_ctx.append(dict(inst=revision, html=REVISION_TEMPLATE.render(template.Context({
                'title': revision.title,
                'html': revision.html,
                'tags': revision.tagname_list(),
        }))))

        if i > 0:
            rev_ctx[i]['diff'] = mark_safe(htmldiff(rev_ctx[i-1]['html'], rev_ctx[i]['html']))
        else:
            rev_ctx[i]['diff'] = mark_safe(rev_ctx[i]['html'])

        if not (revision.summary):
            rev_ctx[i]['summary'] = _('Revision n. %(rev_number)d') % {'rev_number': revision.revision}
        else:
            rev_ctx[i]['summary'] = revision.summary
            
    return render_to_response('revisions_question.html', {
                              'post': post,
                              'revisions': rev_ctx,
                              }, context_instance=RequestContext(request))



