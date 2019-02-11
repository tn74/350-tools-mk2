from typing import Tuple, TextIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from time import time
from hashlib import md5

from tools350 import settings
from tools350.assembler.Assembler import Assembler

HTML_ROOT = '/home/mdd36/tools350/static'


def index(request):
    with open(os.path.join(HTML_ROOT, 'index', 'index.html'), 'r') as html:
        return HttpResponse(''.join(html.readlines()))


def assembler(request):
    with open(os.path.join(HTML_ROOT, 'assembler', 'assembler.html'), 'r') as html:
        return HttpResponse(''.join(html.readlines()))


def wip(request):
    with open(os.path.join(HTML_ROOT, 'wip', 'wip.html')) as html:
        return HttpResponse(''.join(html.readlines()))


@csrf_exempt
def assemble(request):
    if request.method == 'POST':
        assembly_files = [_store_local(f) for f in request.FILES.getlist('assembly', None) if f]
        if assembly_files:
            additional_declarations = {k: v for k, v in zip(Assembler.FIELDS,
                                                            [request.FILES.get(f, None) for f in Assembler.FIELDS]) if v}
            ret = Assembler.assemble_all([x[1] for x in assembly_files], [x[0] for x in assembly_files],
                                         additional_declarations)
            return FileResponse(ret)
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
