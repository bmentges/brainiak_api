# coding: utf-8
import re
import uuid

from brainiak.prefixes import expand_uri, is_compressed_uri, is_uri
from brainiak import triplestore


PATTERN_P = re.compile(r'p(?P<index>\d*)$')  # p, p1, p2, p3 ...
PATTERN_O = re.compile(r'o(?P<index>\d*)$')  # o, o1, o2, o3 ...

XML_LITERAL = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'
XSD_BOOLEAN = u'http://www.w3.org/2001/XMLSchema#boolean'
XSD_BOOLEAN_SHORT = u'xsd:boolean'
XSD_STRING = u'http://www.w3.org/2001/XMLSchema#string'

IGNORED_DATATYPES = [XML_LITERAL, XSD_STRING]


def get_super_properties(bindings):
    super_properties = {}
    for item in bindings:
        if 'super_property' in item:
            key = item['super_property']['value']
            value = item['predicate']['value']
            super_properties[key] = value
    return super_properties


def normalize_term(term, language=""):
    """
    Provided a query term (literal, variable, expanded uri or
    compressed uri), and language (to be applied in literals),
    return the term in the form so it can be used inside a
    SPARQL Query.

    examples:
      (1) http://expanded.predicate -> <http://expanded.predicate>
      (2) compressed:predicate -> compressed:predicate
      (3) "some literal" -> '"some literal"@lang'
      (4) ?variable -> ?variable

    """
    language_tag = u"@%s" % language if language else u""
    if (not term.startswith("?")):
        if (":" in term):
            expanded_term = expand_uri(term)
            if expanded_term != term or is_uri(expanded_term):
                term = u"<%s>" % expanded_term
        else:
            term = u'"%s"%s' % (term, language_tag)
    return term


def is_literal(term):
    return (not term.startswith("?")) and (not ":" in term)


def is_url(term):
    return term.startswith("http")


def has_lang(literal):
    if isinstance(literal, basestring):
        return literal[-3:].startswith("@")
    return False


def create_instance_uri(class_uri):
    """
    Create an unique uri for an instance of the class provided.
    """
    return u"%s/%s" % (class_uri, uuid.uuid4())


def extract_instance_id(instance_uri):
    """
    Extract instance id from an instance URI.
    """
    return instance_uri.split("/")[-1]


def get_one_value(result_dict, key):
    """
    Return first value mapped by 'key' inside the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}]}}
    >>> get_one_value(result_dict, 'key')
    "some value"
    >>> get_one_value(result_dict, 'inexistent_key')
    False
    """
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def filter_values(result_dict, key):
    """
    Return a list of values mapped by 'key' inside the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}, {'key': {'type': 'some type', 'value': 'another value'}}]}}
    >>> filter_values(result_dict, 'key')
    ["some value", "another value"]
    >>> filter_values(result_dict, 'inexistent_key')
    []
    """
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def bindings_to_dict(key_name, bindings):
    """
    Transform the response of a SPARQL query into a dictionary.
    We use the parameter key_name to extract from each binding the value that will become a response key.
    The value of the response is the dictionary returned from the binding.

    For example:
    key_name = 'predicate'
    bindings = {u'head': {u'link': [],
               u'vars': [u'predicate', u'predicate_graph', u'predicate_comment', u'type', u'range', u'title', u'range_graph', u'range_label', u'super_property', u'domain_class']},
               u'results': {u'distinct': False,
                            u'bindings': [
                                {u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                                 u'title': {u'type': u'literal', u'value': u'Nome popular'},
                                 u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                                 u'domain_class': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#Thing'},
                                 u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                                 u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}}]}}

    The expected response is:
       {u'http://www.w3.org/2000/01/rdf-schema#label':
                                {u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                                 u'title': {u'type': u'literal', u'value': u'Nome popular'},
                                 u'predicate_graph': {u'type': u'uri', u'value': u'http://semantica.globo.com/'},
                                 u'domain_class': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#Thing'},
                                 u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                                 u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'}}
    """
    bindings_by_predicate = {}
    for record in bindings['results']['bindings']:
        key_item = record.get(key_name, None)
        if key_item is None:
            continue
        bindings_by_predicate[key_item['value']] = record
    return bindings_by_predicate


def compress_keys_and_values(result_dict, keymap={}, ignore_keys=[], context=None, expand_uri=False):
    """
    Return a list of compressed items of the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}, \
                                                {'key': {'type': 'some type', 'value': 'another value'}}]}}
    >>> compress_keys_and_values(result_dict)
    [{'key': 'some value'}, {'key': 'another value'}]

    Optional params:

    - keymap = {'key': 'renamed_key'}: renames resulting dict 'key' by 'renamed_key'
    - ignore_keys = ['key']: list of keys that shouldn't be returned
    - context (instance of MemorizeContext): shortens URIs according to provided context

    >>> compress_keys_and_values(result_dict, keymap={'key': 'renamed_key'})
    [{'renamed_key': 'some value'}, {'renamed_key': 'another value'}]

    >>> compress_keys_and_values(result_dict, ignore_keys=['key'])
    []

    >>> from brainiak.prefixes import MemorizeContext
    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/value'}}]}}
    >>> context = MemorizeContext()
    >>> compress_keys_and_values(result_dict, context=context)
    [{'key': 'foaf:value'}]

    """
    result_list = []
    for item in result_dict['results']['bindings']:
        row = {}
        for key in item:
            if not key in ignore_keys:
                value = item[key]['value']
                effective_key = keymap.get(key, key)
                if item[key]['type'] == 'uri' and context and effective_key != '@id' and not expand_uri:
                    value = context.shorten_uri(value)
                row[effective_key] = value
        result_list.append(row)
    return result_list


def is_result_empty(result_dict):
    """
    Return True if result_dict['results']['bindings'] has no items, False otherwise.
    """
    return not result_dict['results']['bindings']


INSERT_RESPONSE_PATTERN = re.compile(r'Insert into \<.+?\>, (\d+) \(or less\) triples -- done')


def is_insert_response_successful(response):
    try:
        inserted = response['results']['bindings'][0]['callret-0']['value']
        match = INSERT_RESPONSE_PATTERN.match(inserted)
        if match:
            return int(match.group(1)) > 0
    except (KeyError, TypeError):
        pass
    return False


MODIFY_RESPONSE_PATTERN = re.compile(r'Modify \<.+?\>, delete (\d+) \(or less\) and insert (\d+) \(or less\) triples -- done')


def is_modify_response_successful(response, n_deleted=None, n_inserted=None):
    try:
        inserted = response['results']['bindings'][0]['callret-0']['value']
        match = MODIFY_RESPONSE_PATTERN.match(inserted)
        if match:
            if n_deleted is not None and int(match.group(1)) != n_deleted:
                return False
            if n_inserted is not None and int(match.group(2)) != n_inserted:
                return False
            return True
    except (KeyError, TypeError):
        pass
    return False


def some_triples_deleted(result_dict, graph_uri):
    """
    Return True if result_dict['results']['bindings'][0]['callret-0']['value'] has a message like
    "Delete from <a>, 1 (or less) triples -- done"

    If the message is like "Delete from <a>, 0 triples -- nothing to do" False is returned

    If no patterns matched, raise an Exception, probably Virtuoso message changed

    >>> result_dict = { "head": { "link": [], "vars": ["callret-0"] }, "results": { "distinct": False, "ordered": True, "bindings": [{ "callret-0": { "type": "literal", "value": "Delete from <a>, 1 (or less) triples -- done" }} ] } }
    >>> some_triples_deleted(result_dict)
    >>> True

    """
    try:
        query_result_message = result_dict['results']['bindings'][0]['callret-0']['value']
    except:
        raise UnexpectedResultException(u"Unknown result format: " + unicode(result_dict))
    delete_successful_message = u"Delete from <%s>, ([0-9]*) \(or less\) triples -- done" % graph_uri
    not_found_message = u"0 triples -- nothing to do"

    if re.search(delete_successful_message, query_result_message):
        return True
    elif re.search(not_found_message, query_result_message):
        return False
    else:
        raise UnexpectedResultException("Unknown result format: " + unicode(result_dict))


def is_result_true(result_dict):
    """
    Return result_dict['boolean'] if exists, otherwise returns False
    >>> result_dict = {"head": {"link": []}, "boolean": True}
    >>> is_result_true(result_dict)
    >>> True
    """
    return result_dict.get("boolean", False)


def unpack_tuples(instance_data):
    # retrieve items that map lists and remove them from instance_data
    list_items = [(predicate, object_) for (predicate, object_) in instance_data.items() if isinstance(object_, list)]
    [instance_data.pop(index) for index, value in list_items]

    predicate_object_tuples = instance_data.items()
    for predicate, list_objects in list_items:
        for object_ in list_objects:
            predicate_object_tuples.append((predicate, object_))
    return predicate_object_tuples


def is_reserved_attribute(predicate):
    reserved_words = ["@context"]
    if predicate in reserved_words:
        return True

    reserved_prefix = ["@", "$", "_"]
    if predicate[0] in reserved_prefix:
        return True

    return False


def clean_up_reserved_attributes(instance_data):
    clean_instance = {}
    for key, value in instance_data.items():
        if not is_reserved_attribute(key):
            clean_instance[key] = value

    return clean_instance


def get_predicate_datatype(class_object, predicate_uri):
    predicate = class_object['properties'][predicate_uri]
    if 'range' in predicate:
        return None
    # Without range it is a datatype property

    # Typecasted XMLLiteral is causing bugs on triplestore
    datatype = predicate['datatype']
    if datatype in IGNORED_DATATYPES or expand_uri(datatype) in IGNORED_DATATYPES:
        return ""
    else:
        return datatype


class InvalidSchema(Exception):
    pass


def create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, query_params):
    # TODO-2:
    # lang = query_params["lang"]
    # if lang is "undefined":
    #     lang_tag = ""
    # else:
    #     lang_tag = "@%s" % lang

    instance = u"<%s>" % instance_uri
    predicate_object_tuples = unpack_tuples(instance_data)
    triples = []

    for (predicate_uri, object_value) in predicate_object_tuples:
        if not is_reserved_attribute(predicate_uri):

            try:
                predicate_datatype = get_predicate_datatype(class_object, predicate_uri)
            except KeyError:
                msg = u'Property {0} was not found in the schema of instance {1}'
                raise InvalidSchema(msg.format(predicate_uri, instance_uri))

            predicate_uri_with_brackets = "<%s>" % predicate_uri

            if predicate_datatype is not None:
                # Datatype property
                # TODO refactor to a function to return object_

                # TODO: if literal is string and not i18n, add lang
                if has_lang(object_value):
                    object_ = object_value
                else:
                    if predicate_datatype == XSD_BOOLEAN or predicate_datatype == XSD_BOOLEAN_SHORT:
                        object_value = encode_boolean(object_value)
                    else:
                        object_value = escape_quotes(object_value)

                    if is_uri(predicate_datatype):
                        typecast_template = u'"{0}"^^<{1}>'
                    elif predicate_datatype:
                        typecast_template = u'"{0}"^^{1}'
                    else:
                        typecast_template = u'"{0}"{1}'  # {1} empty not typecasted, e.g. XML_LITERAL

                    object_ = typecast_template.format(object_value, predicate_datatype)
            else:
                # Object property
                # TODO refactor to a function to return object_
                if is_uri(object_value):
                    object_ = u"<%s>" % object_value
                elif is_compressed_uri(object_value, instance_data.get("@context", {})):
                    object_ = object_value
                elif isinstance(object_value, dict):
                    object_ = u"<%s>" % object_value["@id"]
                else:
                    raise InvalidSchema(u'Unexpected value {0} for object property {1}'.format(object_value, predicate_uri))

            validate_value_uniqueness(instance_uri, object_, predicate_uri, class_object, graph_uri, query_params)

            triple = (instance, predicate_uri_with_brackets, object_)
            triples.append(triple)

    return triples


ESCAPED_QUOTES = {
    u'"': u'\\"',
    u"'": u"\\'"
}


def escape_quotes(object_value):
    if isinstance(object_value, basestring):
        escaped_value = object_value
        for char in ESCAPED_QUOTES:
            escaped_value = escaped_value.replace(char, ESCAPED_QUOTES[char])

        return escaped_value
    else:
        return object_value


def encode_boolean(object_value):
    if object_value is False:
        return "false"
    elif object_value is True:
        return "true"
    raise TypeError(u"Could not encode boolean using {0}".format(object_value))


def decode_boolean(object_value):
    if object_value == "0":
        return False
    elif object_value == "1":
        return True
    else:
        raise TypeError(u"Could not decode boolean using {0}".format(object_value))


QUERY_VALUE_EXISTS = u"""
ASK FROM <%(graph_uri)s> {
  ?s a <%(class_uri)s> .
  ?s <%(predicate_uri)s> %(object_value)s
  FILTER (?s != <%(instance_uri)s>)
}
"""


def validate_value_uniqueness(instance_uri, object_value, predicate_uri, class_object, graph_uri, query_params):
    if class_object['properties'][predicate_uri].get("unique_value", False):
        query = QUERY_VALUE_EXISTS % {
            "graph_uri": graph_uri,
            "class_uri": class_object['id'],
            "instance_uri": instance_uri,
            "predicate_uri": predicate_uri,
            "object_value": object_value
        }
        query_result = triplestore.query_sparql(query, query_params.triplestore_config)
        if is_result_true(query_result):
            raise RuntimeError()


def create_implicit_triples(instance_uri, class_uri):
    class_triple = (u"<%s>" % instance_uri, "a", u"<%s>" % class_uri)
    return [class_triple]


TRIPLE = u"""   %s %s %s ."""


def join_triples(triples):
    triples_strings = [TRIPLE % triple for triple in triples]
    return u"\n".join(triples_strings)


PREFIX = u"""PREFIX %s: <%s>"""


def join_prefixes(prefixes_dict):
    prefix_list = []
    for (slug, graph_uri) in prefixes_dict.items():
        if not slug.startswith("@"):
            prefix = PREFIX % (slug, graph_uri)
            prefix_list.append(prefix)
    return u"\n".join(prefix_list)


QUERY_FILTER_LABEL_BY_LANGUAGE = u"""
    FILTER(langMatches(lang(?%(variable)s), "%(lang)s") OR langMatches(lang(?%(variable)s), "")) .
"""


def add_language_support(query_params, language_dependent_variable):
    lang = query_params.get("lang")
    language_tag = "@%s" % lang if lang else ""
    key_name = "lang_filter_%s" % language_dependent_variable
    if language_tag:
        query_params[key_name] = QUERY_FILTER_LABEL_BY_LANGUAGE % {
            "lang": language_tag[1:],  # excludes @
            "variable": language_dependent_variable
        }
    else:
        query_params[key_name] = ""
    return (query_params, language_tag)


class UnexpectedResultException(Exception):
    pass


def extract_po_tuples(query_string_dict):
    # retrieve indexes defined in query strings for pN and oN
    p_indexes = set([PATTERN_P.match(key).group('index') for key in query_string_dict if PATTERN_P.match(key)])
    o_indexes = set([PATTERN_O.match(key).group('index') for key in query_string_dict if PATTERN_O.match(key)])

    only_p_is_defined = p_indexes - o_indexes
    only_o_is_defined = o_indexes - p_indexes
    both_p_and_o_are_defined = o_indexes & p_indexes

    po_list = []

    for index in both_p_and_o_are_defined:
        p_key = u"p{0}".format(index)
        p_value = query_string_dict[p_key]
        o_key = u"o{0}".format(index)
        o_value = query_string_dict[o_key]
        po_list.append((p_value, o_value, index))

    for index in only_p_is_defined:
        p_key = u"p{0}".format(index)
        p_value = query_string_dict[p_key]
        o_value = u"?o{0}".format(index)
        po_list.append((p_value, o_value, index))

    for index in only_o_is_defined:
        p_value = u"?p{0}".format(index)
        o_key = u"o{0}".format(index)
        o_value = query_string_dict[o_key]
        po_list.append((p_value, o_value, index))

    return sorted(po_list)
