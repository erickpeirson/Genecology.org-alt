from django.contrib import admin
from texts.models import Text, Creator
from django import forms
from django.conf.urls import patterns, include, url

from texts.forms import CreatorForm, AddTextForm, TextFormReadonly, \
                        SelectTextMethodForm, TextWizard, \
                        SelectTextRepositoryForm, \
                        SelectTextRepositoryCollectionForm, \
                        SelectTextRepositoryItemsForm

class CreatorInline(admin.TabularInline):
    form = CreatorForm
    model = Text.creator.through
    extra = 1

class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'uri', 'dateCreated')
    inlines = [ CreatorInline, ]
    
    def get_urls(self):
            
        urlpatterns = patterns('',
            url(r'^add/$',
                TextWizard.as_view(),
                name='addText')
        )
        urlpatterns += super(TextAdmin, self).get_urls()
        return urlpatterns

    def save_model(self, request, obj, form, change):
        if change:
           return super(TextAdmin, self).save_form(request, obj, form, change)
        else:
            pass    # Will handle with save_formset

    def save_formset(self, request, form, formset, change):
        if change:  # Don't modify the change (edit) behavior.
            return super(TextAdmin, self).save_formset(request, obj, form, change)
        
        else:   # Adding a new text.
            # Uploading a text file.
            if form.cleaned_data['method'] == 'file':
                content = request.FILES['upload'].read()
                filename = request.FILES['upload'].name
                length = len(content)
                title = form.cleaned_data['title']
                uri = form.cleaned_data['uri']
                dateCreated = form.cleaned_data['dateCreated']
                dateDigitized = form.cleaned_data['dateDigitized']

                text = Text(    uri=uri,
                                title=title,
                                dateCreated=dateCreated,
                                dateDigitized=dateDigitized,
                                content=content,
                                filename=filename,
                                length=length)
                text.save()
                
                instances = formset.save(commit=False)
                for creator in instances:
                    creator.text_id=text.id
                    creator.save()


            # Pulling one or more texts from a repository.
            elif form.cleaned_data['method'] == 'repository':
                pass


admin.site.register(Text, TextAdmin)
