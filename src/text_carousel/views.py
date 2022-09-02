from django.shortcuts import render
from django.views import View
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponseRedirect

from .models import BhsaSlots, BhsaNodes


class HebrewDataProcessor:

    def __init__(self):
        print('initializing!')
        self.called = 0

    def format_word_data(self, node):
        """Format a collection of nodes into front-end data."""
        self.called += 1
        print('called:', self.called)
        node['oslot_list'] = [
            BhsaSlots.objects.get(pk=id_) for id_ in node['oslots']
        ]
        return node


processor = HebrewDataProcessor()


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

        # SETUP INITIAL STUDY SESSION IF NECESSARY
        if 'studySession' not in request.session:
            self.initialize_study_session(request)

        # PROCESS USER INPUT
        try:
            input = request.GET['input']

            # clear session
            if input == 'ArrowDown':
                print('Flushing session cache!')
                request.session.flush()
                self.initialize_study_session(request)

            # change position
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

            # redirect user to the original page to avoid re-sending get requests on refresh
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # RENDER THE PAGE
        except KeyError:
            # GET AND RETURN CURRENT PAGE DATA
            position = request.session['studySession']['position']
            verse_id = request.session['studySession']['verses'][position]
            verse_obj = BhsaNodes.objects.get(pk=verse_id)
            bhsa_nodes = processor.format_word_data(
                model_to_dict(verse_obj)
            )
            return render(request, 'text_carousel/index.html', {'bhsaNode': bhsa_nodes})
