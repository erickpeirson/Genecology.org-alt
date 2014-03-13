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
#    inlines = [ CreatorInline, ]

    def get_urls(self):
        urls = super(TextAdmin, self).get_urls()
        print urls
        my_urls = patterns('',
            (r'^(.+)/add/$', self.textadminview)
        )
        return my_urls + urls

    def textadminview(self, request, **kwargs):
        from django.shortcuts import render_to_response
        from django.template import RequestContext
        print 'asdf'
        return render_to_response('admin/change_form.html',locals(),context_instance=RequestContext(request))
#        if obj is None:
#            do = request.session.get('do', None)
#
#            if do == 'repository':
#                return SelectTextRepositoryForm
#            elif do == 'repository_collections':
#                return SelectTextRepositoryCollectionForm
#            elif do == 'repository_items':
#                return SelectTextRepositoryItemsForm
#            elif do == 'local':
#                self.inlines = [ CreatorInline, ]
#                return AddTextForm
#            return SelectTextMethodForm
#        else:   # TODO: Change this to point to a form that doesn't allow
#                #  editing.
#            return TextFormReadonly

    def add_view(self, request, extra_context=None, **kwargs):
        if request.method == 'POST':
            print 'post'
        else:
            print 'get'

        extra_context = extra_context or {}
        extra_context['show_save'] = False

        return super(TextAdmin, self).add_view(request, extra_context=extra_context, **kwargs)

#    def get_form(self, request, obj=None, **kwargs):
#        if obj is None:
#            do = request.session.get('do', None)
#
#            if do == 'repository':
#                return SelectTextRepositoryForm
#            elif do == 'repository_collections':
#                return SelectTextRepositoryCollectionForm
#            elif do == 'repository_items':
#                return SelectTextRepositoryItemsForm
#            elif do == 'local':
#                self.inlines = [ CreatorInline, ]
#                return AddTextForm
#            return SelectTextMethodForm
#        else:   # TODO: Change this to point to a form that doesn't allow
#                #  editing.
#            return TextFormReadonly

#    def get_urls(self):
#        urls = super(TextAdmin, self).get_urls()
#        my_urls = patterns('',
#            url(
#                r'^add/$',
#                TextWizard.as_view(
#                    [SelectTextMethodForm,
#                     SelectTextRepositoryForm,
#                     SelectTextRepositoryCollectionForm,
#                     SelectTextRepositoryItemsForm ])
#            ),
#
#        )
#        return my_urls + urls

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
