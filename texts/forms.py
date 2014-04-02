from django import forms
from texts.models import Text
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from concepts.models import Concept
from repositories.models import Repository
from repositories.forms import RepositoryChoiceField
from django.forms.widgets import DateInput
from texts.managers import list_collections, list_items, list_bitstreams
import autocomplete_light
import os

HELP_TEXT = {
    'method': 'You can either upload a text from your computer\'s harddrive,' +\
              ' or select one or more texts from a digital repository.',
    'uri':    'Uniform Resource Identifier for this text. If you are'         +\
              ' uploading this text manually, chances are good that no URI'   +\
              ' exists. You can make something up, but it must be unique.',
    'dateCreated': 'The date when the original resource was created. For'     +\
              ' example, the publication date. Must be in YYYY, YYYY-MM, or'  +\
              ' YYYY-MM-DD format.',
    'dateDigitized': 'The date when the resouce was converted to a digital'   +\
              ' format. For example, the date when an OCR extraction was'     +\
              ' performed. Must be in YYYY, YYYY-MM, or YYYY-MM-DD format.',
    'upload': 'Select a file from your computer. Must be a plain text file.',
    'creator': 'Choose one or more creators.'
}

class TextFormBase(forms.ModelForm):
    class Meta:
        model = Text

    def __init__(self, *args, **kwargs):
        super(TextFormBase, self).__init__(*args, **kwargs)
    
        # URI
        self.fields['uri'].label = 'URI'
        self.fields['uri'].help_text = HELP_TEXT['uri']
        # Date Created
        self.fields['dateCreated'] = forms.DateField(input_formats=('%Y',
                                                                    '%Y-%m',
                                                                    '%Y-%m-%d'))
        self.fields['dateCreated'].label = 'Date Created'
        self.fields['dateCreated'].help_text = HELP_TEXT['dateCreated']
        
        # Date Digitized
        self.fields['dateDigitized'] = forms.DateField(input_formats=(
                                                                    '%Y',
                                                                    '%Y-%m',
                                                                    '%Y-%m-%d'))
        self.fields['dateDigitized'].label = 'Date Digitized'
        self.fields['dateDigitized'].help_text = HELP_TEXT['dateDigitized']

class AddTextForm(TextFormBase):
    class Meta(TextFormBase.Meta):
        fields = ['title', 'uri', 'dateCreated', 'dateDigitized', 'upload']
        exclude = ['length', 'content', 'filename', 'creator']

    upload = forms.FileField()
    creator = autocomplete_light.ModelMultipleChoiceField('ConceptAutocomplete')

    def __init__(self, *args, **kwargs):
        super(AddTextForm, self).__init__(*args, **kwargs)

        # Upload
        self.fields['upload'].help_text = HELP_TEXT['upload']

        # Creator
        self.fields['creator'].help_text = HELP_TEXT['creator']

class TextFormReadonly(TextFormBase):
    class Meta(TextFormBase.Meta):
        fields = ['title', 'uri', 'dateCreated', 'dateDigitized',
                  'content', 'length', 'filename']
    
    def __init__(self, *args, **kwargs):
        super(TextFormReadonly, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True
            
        # Filename
        self.fields['filename'].widget.attrs['size'] = 200

class SelectTextMethodForm(forms.Form):
    method_choices = [
                        ('local', 'Upload file'),
                        ('remote', 'Load remote file')
                     ]
    method = forms.ChoiceField(choices=method_choices)

    def save(self, commit=False):
        print 'save'
        super(SelectTextMethodForm, self).save(commit=commit)

class SelectTextRepositoryForm(forms.Form):
    repository = RepositoryChoiceField(queryset=Repository.objects.all())

class SelectTextRepositoryCollectionForm(forms.Form):
    collection = forms.ChoiceField()

    def __init__(self, data=None, *args, **kwargs):
        choices = None
        if 'choices' in kwargs:
            choices = kwargs['choices']
            del kwargs['choices']
        
        super(SelectTextRepositoryCollectionForm, self).__init__(data=data,
                                                                  *args,
                                                                  **kwargs)
        if choices is not None:
            self.fields['collection'] = forms.ChoiceField(choices=choices)

class SelectTextRepositoryItemsForm(forms.Form):
    items = forms.MultipleChoiceField(choices=[('a','a'),],
                                            widget=forms.CheckboxSelectMultiple)
    def __init__(self, data=None, *args, **kwargs):
        choices = None
        if 'choices' in kwargs:
            choices = kwargs['choices']
            del kwargs['choices']
        
        super(SelectTextRepositoryItemsForm, self).__init__(data=data,
                                                                *args,
                                                                **kwargs)
        if choices is not None:
            self.fields['items'] = forms.MultipleChoiceField(choices=choices,
                                            widget=forms.CheckboxSelectMultiple,
                                            initial=[c[0] for c in choices])

class TextWizard(SessionWizardView):
    file_storage = FileSystemStorage()

    template_name='texts/textwizard.html'
    
    def __name__(self):
        return self.__class__.__name__

    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin # Save this so we can use it later.
        opts = admin.model._meta # Yes, I know we could've done Employer._meta, but this is cooler :)
        self.extra_context.update({
            'title': u'Add %s' % force_unicode(opts.verbose_name),
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            'root_path': admin.admin_site.root_path,
            'app_label': opts.app_label,
        })

    def done(self, form_list, **kwargs):
    
        # Handle upload from local file.
        if form_list[0].cleaned_data['method'] == 'local':
            content = form_list[1].cleaned_data['upload'].read()
            filename = form_list[1].cleaned_data['upload'].name
            length = len(content)
            title = form_list[1].cleaned_data['title']
            uri = form_list[1].cleaned_data['uri']
            dateCreated = form_list[1].cleaned_data['dateCreated']
            dateDigitized = form_list[1].cleaned_data['dateDigitized']
            creator = form_list[1].cleaned_data['creator']
            print type(form_list[1].cleaned_data['upload'])
            text = Text(    uri=uri,
                            title=title,
                            dateCreated=dateCreated,
                            dateDigitized=dateDigitized,
                            content=content,
                            filename=filename,
                            length=length)
            text.save()

            for c in creator:
                text.creator.add(c.id)
            text.save()

        # Handle selection of remote files.
        elif form_list[0].cleaned_data['method'] == 'remote':
            from pprint import pprint
            repo = form_list[1].cleaned_data['repository']
            coll = form_list[2].cleaned_data['collection']
            items = form_list[3].cleaned_data['items']
            pprint(list_bitstreams(repo, coll, '11468'))

        return render_to_response('texts/done.html', {
            'form_data': [ form.cleaned_data for form in form_list ],
            'text': text
        })

    def get_form(self, step=None, data=None, files=None):
        form = super(TextWizard, self).get_form(step, data, files)

        if step is None:
            step = self.steps.current

        kwargs = self.get_form_kwargs(step)
        form_class = self.form_list[step]
        
        # Handle Repository selection; generate a list of collections.
        if step == '2':
            method_data = self.get_cleaned_data_for_step('0')
            if method_data['method'] == 'remote':
                r_data = self.get_cleaned_data_for_step('1')
                collections = list_collections(r_data['repository'])
                c_options = [ (c['id'], c['name']) for c in collections ]
                if form_class.__name__ == 'SelectTextRepositoryCollectionForm':
                    kwargs.update({ 'choices': c_options })

        # Handle Collection selection; generate a list of items.
        if step == '3':
            method_data = self.get_cleaned_data_for_step('0')
            if method_data['method'] == 'remote':
                r_data = self.get_cleaned_data_for_step('1')
                c_data = self.get_cleaned_data_for_step('2')
                items = list_items(r_data['repository'], c_data['collection'])
                i_options = [ (i['id'], i['name']) for i in items ]
                kwargs.update({'choices': i_options})

        kwargs.update({
            'data': data,
            'files': files,
            'prefix': self.get_form_prefix(step, form_class),
            'initial': self.get_form_initial(step),
        })

        if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
            # If the form is based on ModelForm or InlineFormSet,
            # add instance if available and not previously set.
            kwargs.setdefault('instance', self.get_form_instance(step))
        elif issubclass(form_class, forms.models.BaseModelFormSet):
            # If the form is based on ModelFormSet, add queryset if available
            # and not previous set.
            kwargs.setdefault('queryset', self.get_form_instance(step))
        return form_class(**kwargs)

def add_remote_text(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    try:
        if cleaned_data['method'] == 'remote':
            return True
    except KeyError:
        pass
    return False

def add_local_text(wizard):
    return not add_remote_text(wizard)

def get_text_form_list(request, form_list=None):
    if form_list is None:
        form_list = [   SelectTextMethodForm,
                        SelectTextRepositoryForm,
                        SelectTextRepositoryCollectionForm,
                        SelectTextRepositoryItemsForm,
                        AddTextForm   ]

    return TextWizard.as_view(form_list=form_list,
                              condition_dict={'1': add_remote_text,
                                              '2': add_remote_text,
                                              '3': add_remote_text,
                                              '4': add_local_text})(request)