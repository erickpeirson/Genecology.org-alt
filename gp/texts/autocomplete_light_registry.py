import autocomplete_light
from models import Creator
from concepts.models import Concept

class ConceptAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choice_label(self, choice):
        return choice.name

autocomplete_light.register(Concept, ConceptAutocomplete)