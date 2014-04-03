from texts.models import Text
from networks.models import Appellation, Relation

def text_appellations(text):
    return Appellation.objects.filter(textposition__text__id=text.id)
    
def text_relations(text):
    return Relation.objects.filter(predicate__textposition__text__id=text.id)