from django.http import HttpResponse, FileResponse, Http404
import os

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


def assemble(request):
    if request.method == 'POST':
        assembly_files = request.FILES.getlist('assembly', None)
        if assembly_files:
            additional_declarations = {k: v for k, v in zip(Assembler.FIELDS,
                                                            [request.FILES.get(f, None) for f in Assembler.FIELDS]) if v}
            ret = Assembler.assemble_all(assembly_files, additional_declarations)
            return FileResponse(ret)
        else:
            return HttpResponse()
    else:
        raise Http404("Endpoint not allowed for GET")
