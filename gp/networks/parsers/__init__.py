import xml.parsers.expat

from pprint import pprint

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class BaseParser(object):
    def parse(self, input):
        if hasattr(input, 'read'):
            result = self.ParseFile(input)
            return result

    def ParseFile(self, file):
        logging.error('BaseParser should not be used directly!')
        return

class XGMMLParser(BaseParser):
    # adapted from https://gist.github.com/informationsea/4284956
    def __init__(self):
        """
        """
        self.appellations = []
        self.relations = []
        
        self._parser = xml.parsers.expat.ParserCreate()
        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._tagstack = list()
 
        self._current_attr = dict()
        self._current_obj = dict()
 
    def _start_element(self, tag, attr):
        """
        
        Arguments:
        - `self`:
        - `tag`:
        - `attr`:
        """
 
        self._tagstack.append(tag)
 
        if tag == 'node' or tag == 'edge':
            self._current_obj = dict(attr)
            self._current_attr = dict()
 
        if tag == 'att' and (self._tagstack[-2] == 'node' or self._tagstack[-2] == 'edge'):
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
        """
        
        Arguments:
        - `self`:
        - `tag`:
        """
        
        if tag == 'node':
            self.appellations.append({  'id':   self._current_obj['id'],
                                        'label':    self._current_obj['label'],
                                        'attributes': self._current_attr })

        elif tag == 'edge':
            self.relations.append({ 'source':   self._current_obj['source'],
                                    'target':   self._current_obj['target'],
                                    'attributes': self._current_attr } )

        self._tagstack.pop()
 
    def ParseFile(self, file):
        """
        
        Arguments:
        - `self`:
        - `file`:
        """
 
        self._parser.ParseFile(file)
        return {'appellations': self.appellations, 'relations': self.relations}

class GraphMLParser(BaseParser):
	def ParseFile(self, file):
		print 'graphml'
		print file.read()

PARSERS = { 'XGMML': XGMMLParser,
            'GraphML': GraphMLParser  }

def parserFactory(format):
    return PARSERS[format]