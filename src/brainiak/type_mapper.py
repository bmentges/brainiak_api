# -*- coding: utf-8 -*-

"This module helps mapping semantic types to our approach of rendering types in json-schema"
from brainiak.prefixes import expand_uri

OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
DATATYPE_PROPERTY = "http://www.w3.org/2002/07/owl#DatatypeProperty"

_MAP_XSD_TO_JSON_TYPE = {
    "rdf:XMLLiteral": "string",
    "rdfs:Literal": "string",
    "xsd:string": "string",
    "xsd:anyURI": "string",
    "xsd:float": "number",
    "xsd:double": "number",
    "xsd:integer": "integer",
    "xsd:nonPositiveInteger": "integer",
    "xsd:nonNegativeInteger": "integer",
    "xsd:negativeInteger": "integer",
    "xsd:positiveInteger": "integer",
    "xsd:long": "integer",
    "xsd:int": "integer",
    "xsd:short": "integer",
    "xsd:byte": "integer",
    "xsd:decimal": "integer",
    "xsd:unsignedLong": "integer",
    "xsd:unsignedInt": "integer",
    "xsd:unsignedShort": "integer",
    "xsd:unsignedByte": "integer",
    "xsd:boolean": "boolean"
}
_MAP_EXPAND_XSD_TO_JSON_TYPE = {expand_uri(k): v for k, v in _MAP_XSD_TO_JSON_TYPE.items()}

# TODO: Use annotations in json-schema and remove this dict

_MAP_JSON_TO_XSD_TYPE = {
    "string": "xsd:string",
    "number": "xsd:double",
    "integer": "xsd:integer",
    "boolean": "xsd:boolean"
}
_MAP_JSON_TO_EXPAND_XSD_TYPE = {k: expand_uri(v) for k, v in _MAP_XSD_TO_JSON_TYPE.items()}

# TODO: support other JSON types:  "object", "array"

_MAP_JSON_TO_PYTHON = {
    "string": unicode,
    "number": float,
    "integer": int,
    "boolean": bool
}

MAP_RDF_TYPE_TO_PYTHON = {
    "rdf:XMLLiteral": basestring,
    "rdfs:Literal": basestring,
    "xsd:string": basestring,
    "xsd:anyURI": basestring,
    "xsd:float": float,
    "xsd:double": float,
    "xsd:integer": int,
    "xsd:nonPositiveInteger": int,
    "xsd:nonNegativeInteger": int,
    "xsd:negativeInteger": int,
    "xsd:positiveInteger": int,
    "xsd:long": int,
    "xsd:int": int,
    "xsd:short": int,
    "xsd:byte": int,
    "xsd:decimal": float,
    "xsd:unsignedLong": int,
    "xsd:unsignedInt": int,
    "xsd:unsignedShort": int,
    "xsd:unsignedByte": int,
    "xsd:boolean": bool
}

MAP_RDF_EXPANDED_TYPE_TO_PYTHON = {expand_uri(k): v for k, v in MAP_RDF_TYPE_TO_PYTHON.items()}
