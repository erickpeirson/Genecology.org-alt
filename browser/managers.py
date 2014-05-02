from texts.models import Text
from networks.models import Appellation, Relation

def text_appellations(text):
    """
    Retrieve appellations for a text.
    
    Parameters
    ----------
    text : :class:`.Text`
    
    Returns
    -------
    list
        A list of :class:`.Appellation` objects.
    """
    
    return Appellation.objects.filter(textposition__text__id=text.id).order_by('-textposition__endposition')
    
def text_relations(text):
    """
    Retrieve relations for a text.
    
    Parameters
    ----------
    text : :class:`.Text`
    
    Returns
    -------
    list
        A list of :class:`.Relation` objects.
    """
    
    return Relation.objects.filter(predicate__textposition__text__id=text.id)

def add_appellations(text, snip=False):
    """
    
    Parameters
    ----------
    text : :class:`.Text`
    
    Returns
    -------
    str
        Content of :class:`.text`\, with annotations.
    """
    
    appellations = text_appellations(text)

    if len(appellations) < 1:
        return content  # Nothing to do.
    
    end_anchor = '</a>'
    start_anchor_base = '<a class="appellation" id="{0}" name="{0}" style="color: rgb(31, 119, 180);">'
    offset = 100

    content = text.content.replace('\r\n', '\n')

    ap_index = {}
    last_start = len(content) + offset + 1
    last_end = len(content) + + offset + 1
    last_start_anchor = ''
    positions = []

    if snip:
        snippets = []

    for ap in appellations:

        end = ap.textposition.endposition
        start = ap.textposition.startposition

        if start < end < last_start:

            start_anchor = start_anchor_base.format(ap.id)
            
            if snip:
                if end + offset > last_start - offset:
                    e_offset = last_end + len(start_anchor) + offset
                else:
                    e_offset = offset
                
                c_e = content[:end] + end_anchor + content[end:end+e_offset]
                c_s = c_e[start-offset:start] + start_anchor + c_e[start:]

                if end + offset > last_start - offset:
                    snippets[-1] = c_s
                else:
                    snippets.append(c_s)
                
            content = content[:end] + end_anchor + content[end:]
            content = content[:start] + start_anchor + content[start:]
            
            last_start = start
            last_end = end
            last_start_anchor = start_anchor
    if snip:
        snippets.reverse()
        return ''.join([ '<div class="snippet">... {0} ...</div>'.format(s) for s in snippets ])
    return content