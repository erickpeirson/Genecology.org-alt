from django import forms

from .models import *
from .parsers import GraphMLParser
from . import processors

class NetworkForm(forms.ModelForm):
    data_file = forms.FileField(
        help_text='Select a data file to add additional annotation data to'+\
                  ' this network. The data will be processed, and a new '  +\
                  ' accession will be created.')
    data_format = forms.ChoiceField(choices=processors.processor_choices)

    class Meta:
        model = Network
        exclude = []

    def save(self, commit=True):
        """
        Passes uploaded data in ``data_file`` to a processor in 
        :mod:`.processors` based on the specified ``data_format``.
        
        TODO: Handle exceptions.
        """
        
        network = super(NetworkForm, self).save(commit=commit)
        network.save()
        processor_name = self.cleaned_data.get('data_format', None)
        processor = getattr(processors, processor_name)()
        data = self.cleaned_data.get('data_file', None)
        nodes, edges, evidence = processor.process(data.read(), network.id)
        
        return network
    
class LayoutForm(forms.ModelForm):
    layout_file = forms.FileField(
        help_text='Select a GraphML file containing node positions for the' +\
                  ' specified network.')
                  
    def save(self, commit=True):
        layout = super(LayoutForm, self).save(commit)
        layout.save()
        
        network = self.cleaned_data['describes']
        layout_file = self.cleaned_data.get('layout_file', None)
        return process_layout(layout, layout_file)
    
    class Meta:
        model = Layout
        exclude = []

def process_layout(layout, file):
    """
    Extract positional information from a network file, and create a new Layout.
    
    The nodes described in the network file should have IDs corresponding to
    nodes in an existing :class:`.Network` .
    
    Parameters
    ----------
    layout : :class:`.Layout`
        .
    file : str
        Path to a network file (e.g. a GraphML file).
    format : str
        Network data format (e.g. XGMML, GraphML)
    
    Returns
    -------
    :class:`.Layout`
        The resulting :class:`.Layout` object.
    """

    parser = GraphMLParser()
    data = parser.parse(file)
    
    for n in data['nodes']:
        # Find Node
        # TODO: handle exceptions (not found).
        node = Node.objects.get(pk=n['id'])
        
        # Create and associate a NodePosition.
        if 'x' in n['attributes'] and 'y' in n['attributes']:
            pos = NodePosition( describes=node,
                                x = n['attributes']['x'],
                                y = n['attributes']['y'],
                                part_of = layout )
            pos.save()

    return layout


