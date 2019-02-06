from django.http import HttpResponse
import os

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
