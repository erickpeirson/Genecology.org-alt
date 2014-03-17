import autocomplete_light
autocomplete_light.autodiscover()
from django.contrib import admin
from texts.models import Text
from django import forms
from django.conf.urls import patterns, include, url

from texts.forms import AddTextForm, TextFormReadonly, \
                        SelectTextMethodForm, TextWizard, \
                        SelectTextRepositoryForm, \
                        SelectTextRepositoryCollectionForm, \
                        SelectTextRepositoryItemsForm

class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'uri', 'dateCreated')
#    inlines = [ CreatorInline, ]

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^add/$',
                'texts.forms.get_text_form_list',
                name='addText')
        )
        urlpatterns += super(TextAdmin, self).get_urls()
        return urlpatterns

admin.site.register(Text, TextAdmin)
