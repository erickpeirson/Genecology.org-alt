from django.conf.urls import patterns, url

from browser import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'texts/(?P<text_id>.*?)/$', views.display_text, name='display_text'),
    url(r'texts', views.list_texts, name='texts'),   
    url(r'geographic', views.geographic, name='geographic'),
)