# -*- coding: utf-8 -*-

_PREFIXES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'owl':  'http://www.w3.org/2002/07/owl#"owl="http://www.w3.org/2002/07/owl#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
    'upper': 'http://semantica.globo.com/upper/',
    'schema': 'http://schema.org/',
    'dbpedia': 'http://dbpedia.org/ontology/',
    'time': 'http://www.w3.org/2006/time#',
    'event': 'http://purl.org/NET/c4dm/event.owl#',
    'place': 'http://semantica.globo.com/place/',
    'person': 'http://semantica.globo.com/person/',
    'organization': 'http://semantica.globo.com/organization/',
    'act': 'http://semantica.globo.com/data/Activity/'
}

_URIS = {v:k for k,v in _PREFIXES.items()}

def uri_to_prefix(uri):
    return _URIS[uri]

def prefix_to_uri(prefix):
    return _PREFIXES[prefix]

