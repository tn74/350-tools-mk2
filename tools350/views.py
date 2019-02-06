from django.http import HttpResponse
import os

HTML_ROOT = '/home/mdd36/tools350/static'


def root(request):
    with open(os.path.join(HTML_ROOT, 'index.html'), 'r') as html:
        return HttpResponse(''.join(html.readlines()))
