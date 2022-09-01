from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import BhsaSlots, BhsaNodes


def format_word_data(nodes):
    """Format a collection of nodes into front-end data."""
    word_data = []
    for node in nodes:
        node['oslot_list'] = [
            BhsaSlots.objects.get(pk=id_) for id_ in node['oslots']
        ]
        word_data.append(node)
    return word_data


def test(request, book, chapter):
    bhsa_objects = BhsaNodes.objects.filter(
        book=book,
        chapter=chapter,
        otype='verse',
    )
    bhsa_nodes = format_word_data(
        bhsa_objects.values()
    )
    context = {'bhsa_nodes': bhsa_nodes}
    return render(request, 'text_carousel/test.html', context)


def index(request):
    template = render_to_string('text_carousel/index.html')
    return HttpResponse(template)
