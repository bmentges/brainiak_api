# -*- coding: utf-8 -*-

"This module helps mapping semantic types to our approach of rendering types in json-schema"

OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
DATATYPE_PROPERTY = "http://www.w3.org/2002/07/owl#DatatypeProperty"

_MAP_XSD_TO_JSON_TYPE = {
    "rdf:XMLLiteral": "string",
    "rdfs:Literal": "string",
    "xsd:string": "string",
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


# TODO: support other JSON types: "boolean", "object", "array"
