from django.shortcuts import render
from django.views import View
from django.forms.models import model_to_dict
from django.http import HttpRequest

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


class Index(View):

    @staticmethod
    def initialize_study_session(request):
        print('Setting up new study session!')
        nodes_list = sorted(
            BhsaNodes.objects.filter(
                book='Genesis',
                chapter=1,
                otype='verse',
            ).values_list('node', flat=True)
        )
        request.session['studySession'] = {
            'position': 0,
            'verses': nodes_list,
        }

    @staticmethod
    def format_word_data(node):
        """Format a collection of nodes into front-end data."""
        node['oslot_list'] = [
            BhsaSlots.objects.get(pk=id_) for id_ in node['oslots']
        ]
        return node

    def get(self, request):

        # SETUP INITIAL STUDY SESSION
        if 'studySession' not in request.session:
            self.initialize_study_session(request)

        # PROCESS USER INPUT
        try:
            input = request.GET['input']
        except KeyError:
            input = ''

        # clear session
        if input == 'ArrowDown':
            print('Flushing session cache!')
            request.session.flush()
            self.initialize_study_session(request)

        # advance position
        elif input in {'ArrowRight', 'ArrowLeft'}:

            print('position:', request.session['studySession']['position'])

            session_dict = request.session['studySession']
            if input == 'ArrowRight':
                session_dict['position'] = min(
                    session_dict['position'] + 1,
                    len(session_dict['verses']) - 1
                )
            else:
                session_dict['position'] = max(0, session_dict['position'] - 1)
            request.session['studySession'] = session_dict

        # GET AND RETURN CURRENT PAGE DATA
        position = request.session['studySession']['position']
        verse_id = request.session['studySession']['verses'][position]
        verse_obj = BhsaNodes.objects.get(pk=verse_id)
        bhsa_nodes = self.format_word_data(
            model_to_dict(verse_obj)
        )
        return render(request, 'text_carousel/index.html', {'bhsaNode': bhsa_nodes})
