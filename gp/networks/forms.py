"""
forms for Networks app
"""

from django import forms
from django.contrib import admin
#from django.forms.extras.widgets import CheckboxSelectMultiple

from networks.models import Dataset, Network, Node, Edge, Appellation,  \
                            Relation, NetworkLink

from networks.managers import DatasetManager


import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

formats = [ 'XGMML', 'GraphML' ]

class DatasetAdminForm(forms.ModelForm):
    upload = forms.FileField()
    
    # TODO: should generate formats list from registered parsers.
    format = forms.ChoiceField([ (format,format) for format in formats ])
    
    class Meta:
        model = Dataset
        exclude = ['appellations', 'relations' ]


#    def __init__(self, *args, **kwargs):
#        super(DatasetAdminForm, self).__init__(*args, **kwargs)
#        self.fields['appellations'].

    def save(self, commit=True, **kwargs):
        """
        send to parser based on format, which returns apellations and relations
        send As and Rs to handlers that check for nodes and edges in network, and
        create if necessary
        """

        instance = super(DatasetAdminForm, self).save(commit=False)
        instance.save()
        d_manager = DatasetManager(instance)
        instance = d_manager.add_dataset(self.cleaned_data, self.data)
        instance.save()
        
        return instance