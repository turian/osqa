from django.shortcuts import render_to_response
from django.template import RequestContext
from forum.views.admin import super_user_required
import importer
from zipfile import ZipFile

@super_user_required
def sximporter(request):
    list = []
    if request.method == "POST" and "dump" in request.FILES:
        dump = ZipFile(request.FILES['dump'])
        importer.sximport(dump, request.POST)
        dump.close()

    return render_to_response('modules/sximporter/page.html', {
        'names': list
    }, context_instance=RequestContext(request))