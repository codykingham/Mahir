"""Make urls available from text carousel app."""

from django.urls import path

from .views import Index

app_name = 'text_carousel'

urlpatterns = [
    path('', Index.as_view(), name='index'),
]
