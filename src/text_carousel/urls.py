"""Make urls available from text carousel app."""

from django.urls import path

from .views import test, index

app_name = 'text_carousel'

urlpatterns = [
    path('', index, name='index'),
    path('test/<str:book>/<int:chapter>', test, name='test'),
]
