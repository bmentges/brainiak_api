# -*- coding: utf-8 -*-

"This module helps mapping semantic types to our approach of rendering types in json-schema"
from brainiak.prefixes import shorten_uri

OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
DATATYPE_PROPERTY = "http://www.w3.org/2002/07/owl#DatatypeProperty"

_MAP_XSD_TO_JSON_TYPE = {
    "xsd:string": "string",
    "xsd:float": "number",
    "xsd:integer": "integer",
    "xsd:XMLLiteral": "any"
}


def items_from_type(predicate_type):
    if predicate_type == OBJECT_PROPERTY:
        return {"type": "string", "format": "uri"}


def items_from_range(range_uri):
    short_range = shorten_uri(range_uri)
    if short_range == 'xsd:date':
        return {"type": "string", "format": "date"}
    else:
        return {"type": _MAP_XSD_TO_JSON_TYPE.get(short_range, "any")}

# TODO: support other JSON types: "boolean", "object", "array"
