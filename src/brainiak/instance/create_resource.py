from brainiak.prefixes import is_compressed_uri, is_uri, shorten_uri
from brainiak.utils.sparql import create_instance_uri, has_lang


# TODO: test
def create_instance(query_params, instance_data):
    class_uri = query_params["class_uri"]
    instance_uri = create_instance_uri(class_uri)

    triples = create_explicit_triples(instance_uri, instance_data)
    implicit_triples = create_implicit_triples(instance_uri, class_uri)
    triples.extend(implicit_triples)
    string_triples = querify_triples(triples)

    # prefixes
    # build insert query
    return "ok"


def create_implicit_triples(instance_uri, class_uri):
    class_triple = ("<%s>" % instance_uri, "a", "<%s>" % class_uri)
    return [class_triple]


def unpack_tuples(instance_data):
    # retrieve items that map lists and remove them from instance_data
    list_items = [(predicate, object_) for (predicate, object_) in instance_data.items() if isinstance(object_, list)]
    [instance_data.pop(index) for index, value in list_items]

    predicate_object_tuples = instance_data.items()
    for predicate, list_objects in list_items:
        for object_ in list_objects:
            predicate_object_tuples.append((predicate, object_))
    return predicate_object_tuples


def create_explicit_triples(instance_uri, instance_data):
    # TODO-2:
    # lang = query_params["lang"]
    # if lang is "undefined":
    #     lang_tag = ""
    # else:
    #     lang_tag = "@%s" % lang

    instance = "<%s>" % instance_uri
    predicate_object_tuples = unpack_tuples(instance_data)
    triples = []

    for (predicate_uri, object_value) in predicate_object_tuples:
        if predicate_uri != "@context":

            # predicate: has to be uri (compressed or not)
            predicate = shorten_uri(predicate_uri)
            if is_uri(predicate):
                predicate = "<%s>" % predicate_uri

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


TRIPLE = """   %s %s %s ."""


def querify_triples(triples):
    triples_strings = [TRIPLE % triple for triple in triples]
    return "\n".join(triples_strings)


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
