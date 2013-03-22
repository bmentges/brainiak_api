from brainiak.prefixes import is_compressed_uri, is_uri, shorten_uri
from brainiak.utils.sparql import create_instance_uri, has_lang


def create_instance(query_params, instance_data):
    instance_uri = create_instance_uri(query_params["class_uri"])
    # create_explicit_triples(instance_uri, instance_data)
    # implicit triples (instance_uri a class_uri - are there more?)
    # prefixes
    # build insert query 
    return "ok"


def create_explicit_triples(instance_uri, instance_data):
    # TODO-2:
    # lang = query_params["lang"]
    # if lang is "undefined":
    #     lang_tag = ""
    # else:
    #     lang_tag = "@%s" % lang

    instance = "<%s>" % instance_uri

    triples = []
    for (predicate_uri, object_value) in instance_data.items():
        if predicate_uri != "@context":

            # predicate: has to be uri (compressed or not)
            predicate = shorten_uri(predicate_uri)
            if is_uri(predicate):
                predicate = "<%s>" % predicate_uri

            # TODO: object is a list
            # object: can be uri (compressed or not) or literal
            if is_uri(object_value):
                object_ = "<%s>" % object_value
            elif is_compressed_uri(object_value, instance_data.get("@context", {})):
                object_ = object_value
            else:
                # TODO: add literal type
                # TODO-2: if literal is string and not i18n, add lang
                if has_lang(object_value):
                    object_ = object_value
                else:
                    object_ = '"%s"' % object_value
            triple = (instance, predicate, object_)
            triples.append(triple)

    return triples


# TODO: test
TRIPLE = """   %(subject)s %(predicate)s %(object)s ."""
def querify_triples():
    pass


# TODO: test
PREFIX = """PREFIX %(slug)s: <%(graph_uri)s>"""


# TODO: test
QUERY_INSERT_TRIPLES = """
%(prefix)s
INSERT DATA INTO <%(graph_uri)s>
{
%(triples)s
}
"""
