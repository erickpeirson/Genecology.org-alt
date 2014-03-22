"""
forms for Networks app
"""

from django import forms
from django.contrib import admin
from networks.managers import DatasetManager
from networks.models import Dataset, Network, Node, Edge, Appellation,  \
                            Relation, NetworkLink
import networks.parsers as parsers

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class DatasetAdminForm(forms.ModelForm):
    upload = forms.FileField()
    
    # TODO: should generate formats list from registered parsers.
    format = forms.ChoiceField([ (fmt,fmt) for fmt in parsers.PARSERS.keys() ])
    
    class Meta:
        model = Dataset
        exclude = ['appellations', 'relations' ]

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