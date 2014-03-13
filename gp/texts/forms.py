from django import forms
from texts.models import Text, Creator
#from django.contrib.formtools.wizard import FormWizard
from django.contrib.formtools.wizard.views import SessionWizardView

from concepts.models import Concept
from repositories.models import Repository
from repositories.forms import RepositoryChoiceField
from django.forms.widgets import DateInput
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
    'upload': 'Select a file from your computer. Must be a plain text file.'
}

class CreatorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class CreatorForm(forms.ModelForm):
    class Meta:
        model = Text.creator.through

    concept = CreatorChoiceField(queryset=Concept.objects \
                                                     .filter(type='E21 Person'))

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
        fields = ['method', 'title', 'uri', 'dateCreated', 'dateDigitized',
                  'upload']
        exclude = ['length', 'content', 'filename', 'creator']
    
    method = forms.ChoiceField(choices=[
                                    ('file', 'Upload local file'),
                                    ('repo', 'Load file(s) from repository')
                                ])
    upload = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(AddTextForm, self).__init__(*args, **kwargs)
        
        # Method
        self.fields['method'].help_text = HELP_TEXT['method']

        # Upload
        self.fields['upload'].help_text = HELP_TEXT['upload']

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
#    method = forms.CharField(max_length=200)

    def save(self, commit=False):
        print 'save'
        #super(SelectTextMethodForm, self).save(commit=commit)

class SelectTextRepositoryForm(forms.Form):
    repository = RepositoryChoiceField(queryset=Repository.objects)

class SelectTextRepositoryCollectionForm(forms.Form):
    collection = forms.ChoiceField()

class SelectTextRepositoryItemsForm(forms.Form):
    items = forms.MultipleChoiceField(choices=[('a','a'),],
                                            widget=forms.CheckboxSelectMultiple)

class TextWizard(SessionWizardView):
    form_list = [   SelectTextMethodForm,
                    SelectTextRepositoryForm,
                    SelectTextRepositoryCollectionForm,
                    SelectTextRepositoryItemsForm]
    template_name='texts/textwizard.html'
    
    def __name__(self):
        return self.__class__.__name__

    def done(self, request, form_list):
        print request
        print form_list

    def get_context_data(self, form, **kwargs):
        context = super(TextWizard, self).get_context_data(form=form, **kwargs)
#        if self.steps.current == 'my_step_name':
        context['opts'] = { 'app_list': ['asdf'],'app_label':'fdsa' }
        return context