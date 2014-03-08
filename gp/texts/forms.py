from django import forms
from texts.models import Text, Creator
from concepts.models import Concept
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
                ('repo', 'Load file(s) from repository') ])
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
