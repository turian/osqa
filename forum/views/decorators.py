from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template import RequestContext

def render(template=None, tab=None):
    def decorator(func):
        def decorated(request, *args, **kwargs):
            context = func(request, *args, **kwargs)

            if tab is not None:
                context['tab'] = tab

            return render_to_response(context.pop('template', template), context, context_instance=RequestContext(request))
        return decorated
    return decorator

def list(paginate, default_page_size):
    def decorator(func):
        def decorated(request, *args, **kwargs):
            context = func(request, *args, **kwargs)

            pagesize = request.utils.page_size(default_page_size)
            page = int(request.GET.get('page', 1))

            big_list = context[paginate]
            paginator = Paginator(big_list, pagesize)

            page_obj = paginator.page(page)
            context[paginate] = page_obj.object_list

            base_path = context.get('base_path', None) or request.path
            sort = request.utils.sort_method('')

            context["pagination_context"] = {
                'is_paginated' : True,
                'pages': paginator.num_pages,
                'page': page,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous': page_obj.previous_page_number(),
                'next': page_obj.next_page_number(),
                'base_url' : "%s%ssort=%s&" % (base_path, ('?' in base_path) and '&' or '?', sort),
                'pagesize' : pagesize
            }

            context['sort_context'] = {
                'base_url': "%s%ssort=" % (base_path, ('?' in base_path) and '&' or '?'),
                'current': sort,
            }

            return context
        return decorated
    return decorator


def command(func):
    def decorated(request, *args, **kwargs):
        try:
            response = func(request, *args, **kwargs)
            response['success'] = True
        except Exception, e:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            response = {
                'success': False,
                'error_message': str(e)
            }

        if request.is_ajax():
            return HttpResponse(simplejson.dumps(response), mimetype="application/json")
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return decorated