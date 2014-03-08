from django import forms
from concepts.models import Concept, ConceptAuthority

class AddConceptForm(forms.ModelForm):
    class Meta:
        model = Concept
        exclude = ['type', 'equalto', 'similarto', 'location', 'name']
    authority = forms.ChoiceField()
    uri = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        # Populate ConceptAuthority choices from existing objects.
        super(AddConceptForm, self).__init__(*args, **kwargs)
        authority_choices = ConceptAuthority.objects.values_list('id', 'name')
        self.fields['authority'].choices = authority_choices
