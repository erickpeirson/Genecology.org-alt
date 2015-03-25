import networkx as nx
from xml.etree import cElementTree as ET

class GraphMLWriter(nx.GraphMLWriter):
    def get_key(self, name, attr_type, scope, default):
        """
        Modified to use attribute name as key, rather than numeric ID.
        """
        keys_key = (name, attr_type, scope)
        try:
            return self.keys[keys_key]
        except KeyError:
            new_id = name
            self.keys[keys_key] = new_id
            key_kwargs = {"id":new_id,
                          "for":scope,
                          "attr.name":name, 
                          "attr.type":attr_type}
            key_element=ET.Element("key",**key_kwargs)

            # add subelement for data default value if present
            if default is not None:
                default_element=ET.Element("default")
                default_element.text=make_str(default)
                key_element.append(default_element)
            self.xml.insert(0,key_element)
        return new_id
    
    def add_data(self, name, element_type, value, 
                 scope="all", 
                 default=None):
        """
        Modified to support lists (just flattens to string).
        """
        if element_type is list:
            value = str(value)
            element_type = type(value)

        if element_type not in self.xml_type:
            raise nx.NetworkXError('GraphML writer does not support '
                                   '%s as data values.'%element_type)
        key_id = self.get_key(name, self.xml_type[element_type], scope, default)
        data_element = ET.Element("data", key=key_id)
        data_element.text = nx.utils.make_str(value)
        return data_element