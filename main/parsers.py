import xml.parsers.expat
from networkx.readwrite.graphml import GraphMLReader

class VogonXGMMLParser(object):
    def __init__(self):
        """
        """
        self.nodes = []
        self.edges = []
        
        self._parser = xml.parsers.expat.ParserCreate()
        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._tagstack = list()
 
        self._current_attr = dict()
        self._current_obj = dict()
 
    def _start_element(self, tag, attr):
        self._tagstack.append(tag)
 
        if tag == 'node' or tag == 'edge':
            self._current_obj = dict(attr)
            self._current_attr = dict()
 
        if tag == 'att' and self._tagstack[-2] in ['node','edge']:
            if attr['type'] == 'string':
                self._current_attr[attr['name']] = str(attr['value'])
            elif attr['type'] == 'real':
                self._current_attr[attr['name']] = float(attr['value'])
            elif attr['type'] == 'integer':
                self._current_attr[attr['name']] = int(attr['value'])
            elif attr['type'] == 'boolean':
                self._current_attr[attr['name']] = bool(attr['value'])
            else:
                raise NotImplementedError(attr['type'])
 
    def _end_element(self, tag):
        if tag == 'node':
            self.nodes.append(  {   'id':   self._current_obj['id'],
                                    'label':    self._current_obj['label'],
                                    'attributes': self._current_attr
                                    })
        elif tag == 'edge':
            self.edges.append(  {   'source':   self._current_obj['source'],
                                    'target':   self._current_obj['target'],
                                    'attributes': self._current_attr
                                    })
        self._tagstack.pop()
 
    def ParseFile(self, file):
        """
        Yields nodes and edges from a XGMML file.
        
        Parameters
        ----------
        file : str
            Path to a GraphML file.
            
        Returns
        -------
        dict
            Contains lists of 'nodes' and 'edges'.
        """
 
        self._parser.ParseFile(file)
        return {'appellations': self.nodes, 'relations': self.edges}

    def Parse(self, buffer):
        self._parser.Parse(buffer)
        return {'appellations': self.nodes, 'relations': self.edges}


class GraphMLParser(object):
    def __init__(self):
        self.reader = GraphMLReader(str)
    
    def _get_nodes(self):
        parsed_nodes = self.graph.nodes(data=True)
        nodes = []
        for n in parsed_nodes:
            id = n[0]
            
            # Label.
            if 'label' in n[1]: label = n[1]['label']
            else: label = id

            # Attributes.
            attributes = { k:v for k,v in n[1].iteritems() if k != 'label'}

            nodes.append({  'id': id,
                            'label': label,
                            'attributes': attributes })
        return nodes
    
    def _get_edges(self):
        parsed_edges = self.graph.edges(data=True)
        edges = []
        for e in parsed_edges:
            source = e[0]
            target = e[1]
            attributes = { k:v for k,v in e[2].iteritems() }
            
            edges.append({  'source': source,
                            'target': target,
                            'attributes': attributes})
        
        return edges
    
    def parse(self, input):
        """
        
        Arguments
        ---------
        input : File-like
            Contains XML data to be parsed.
        """
        
        if hasattr(input, 'read'):
            result = self.ParseFile(input)
            return result

    def ParseFile(self, file):
        """
        Yields nodes and edges from a GraphML file.
        
        Parameters
        ----------
        file : str
            Path to a GraphML file.
            
        Returns
        -------
        dict
            Contains lists of 'nodes' and 'edges'.
        """
        
        self.graph = list(self.reader(file))[0]
        return {'nodes': self._get_nodes(), 'edges': self._get_edges()}

