from brainiak import triplestore
from brainiak.prefixes import is_compressed_uri, is_uri, shorten_uri
from brainiak.utils.sparql import create_instance_uri, has_lang


# TODO: test
def create_instance(query_params, instance_data):
    class_uri = query_params["class_uri"]
    instance_uri = create_instance_uri(class_uri)

    triples = create_explicit_triples(instance_uri, instance_data)
    implicit_triples = create_implicit_triples(instance_uri, class_uri)
    triples.extend(implicit_triples)
    string_triples = join_triples(triples)

    prefixes = instance_data.get("@context", {})
    string_prefixes = join_prefixes(prefixes)
    response = query_create_instances(string_triples, string_prefixes, query_params["graph_uri"])
    return instance_uri

{u'head': {u'link': [], u'vars': [u'callret-0']}, u'results': {u'distinct': False, u'bindings': [{u'callret-0': {u'type': u'literal', u'value': u'Insert into <http://semantica.globo.com/place/>, 7 (or less) triples -- done'}}], u'ordered': True}}


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


def join_triples(triples):
    triples_strings = [TRIPLE % triple for triple in triples]
    return "\n".join(triples_strings)


PREFIX = """PREFIX %s: <%s>"""


def join_prefixes(prefixes_dict):
    prefix_list = []
    for (slug, graph_uri) in prefixes_dict.items():
        prefix = PREFIX % (slug, graph_uri)
        prefix_list.append(prefix)
    return "\n".join(prefix_list)


QUERY_INSERT_TRIPLES = """
DEFINE input:inference <http://semantica.globo.com/place/ruleset>
%(prefix)s
INSERT DATA INTO <%(graph_uri)s>
{
%(triples)s
}
"""


def query_create_instances(triples, prefix, graph_uri):
    query = QUERY_INSERT_TRIPLES % {"triples": triples, "prefix": prefix, "graph_uri": graph_uri}
    return triplestore.query_sparql(query)
