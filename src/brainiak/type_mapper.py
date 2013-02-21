# -*- coding: utf-8 -*-

"This module helps mapping semantic types to our approach of rendering types in json-schema"

OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
DATATYPE_PROPERTY = "http://www.w3.org/2002/07/owl#DatatypeProperty"

def items_from_type(predicate_type):
    if predicate_type == OBJECT_PROPERTY:
        return {"type": "string", "format": "uri"}

_MAP_XSD_TO_JSON_TYPE = {
    "string"
    "number"
    "intenger"
    "boolean"
    "object"
    "array"
}

