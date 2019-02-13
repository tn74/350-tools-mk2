from typing import Tuple, Iterable
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
import os
from time import time
from hashlib import md5

from django.shortcuts import render

from tools350 import settings
from tools350.assembler.Assembler import Assembler

HTML_ROOT = '/home/mdd36/tools350/static'
HTML_ROOT_LOCAL = '/Users/matthew/Documents/SchoolWork/TA/ECE350/2019s/350_tools_mk2/static'



def find(path: Iterable[str]):
    try:
        with open(os.path.join(HTML_ROOT, *path), 'r') as html:
            return HttpResponse(''.join(html.readlines()))
    except FileNotFoundError:
        with open(os.path.join(HTML_ROOT_LOCAL, *path), 'r') as html:
            return HttpResponse(''.join(html.readlines()))


def index(request):
    return find(('index', 'index.html'))


def assembler(request):
    return render(request, 'assembler.html', {})


def wip(request):
    return find(('wip', 'wip.html'))


def bugs_features(request):
    return find(('bugs', 'bugs.html'))


def help(request):
    return find(('help', 'help.html'))


def assemble(request):
    if request.method == 'POST':
        assembly_files = [_store_local(f) for f in request.FILES.getlist('assembly', None) if f]
        if assembly_files:
            additional_declarations = {k: _store_local(v)[1] for k, v in zip(Assembler.FIELDS,
                                                                             [request.FILES.get(f, None) for f in
                                                                              Assembler.FIELDS]) if v}

            ret = Assembler.assemble_all([x[1] for x in assembly_files], [x[0] for x in assembly_files],
                                         additional_declarations)

            response = HttpResponse(content_type="application/zip")
            response["Content-Disposition"] = "attachment; filename=mifs.zip"
            ret.seek(0)
            response.write(ret.read())

            [os.remove(x[1]) for x in assembly_files]
            [os.remove(x) for x in [y for _, y in additional_declarations.items()]]

            return response
        else:
            return Http404("No assembly files")
    else:
        raise Http404("Endpoint not allowed for GET")


def _store_local(filelike: InMemoryUploadedFile) -> Tuple[str, str]:
    name = filelike.name + str(time())
    m = md5()
    m.update(name.encode('utf-8'))
    ret_name: str = m.hexdigest()
    path = 'tmp/' + ret_name

    with default_storage.open(path, 'wb+') as destination:
        for chunk in filelike.chunks():
            destination.write(chunk)
    return filelike.name, os.path.join(settings.MEDIA_ROOT, path)
