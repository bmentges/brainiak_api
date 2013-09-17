# coding: utf-8
import re
import uuid
from brainiak.prefixes import expand_uri, is_compressed_uri, is_uri, PrefixError, shorten_uri


PATTERN_P = re.compile(r'p(?P<index>\d*)$')  # p, p1, p2, p3 ...
PATTERN_O = re.compile(r'o(?P<index>\d*)$')  # o, o1, o2, o3 ...


def get_super_properties(context, bindings):
    super_properties = {}
    for item in bindings:
        if 'super_property' in item:
            key = context.normalize_uri_key(item['super_property']['value'])
            value = context.normalize_uri_value(item['predicate']['value'])
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
    language_tag = "@%s" % language if language else ""
    if (not term.startswith("?")):
        if (":" in term):
            try:
                term = "<%s>" % expand_uri(term)
            except PrefixError:
                pass
        else:
            term = '"%s"%s' % (term, language_tag)
    return term


def is_literal(term):
    return (not term.startswith("?")) and (not ":" in term)


def is_url(term):
    return term.startswith("http")


def has_lang(literal):
    return literal[-3:].startswith("@")


def create_instance_uri(class_uri):
    """
    Create an unique uri for an instance of the class provided.
    """
    return "%s/%s" % (class_uri, uuid.uuid4())


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


def compress_keys_and_values(result_dict, keymap={}, ignore_keys=[], context=None):
    """
    Return a list of compressed items of the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}},
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
                if item[key]['type'] == 'uri' and context:
                    value = context.shorten_uri(value)
                row[keymap.get(key, key)] = value
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

    >>> result_dict = { "head": { "link": [], "vars": ["callret-0"] }, "results": { "distinct": false, "ordered": true, "bindings": [{ "callret-0": { "type": "literal", "value": "Delete from <a>, 1 (or less) triples -- done" }} ] } }
    >>> zero_triples_deleted(result_dict)
    >>> True

    """
    try:
        query_result_message = result_dict['results']['bindings'][0]['callret-0']['value']
    except:
        raise UnexpectedResultException("Unknown result format: " + str(result_dict))
    delete_successful_message = "Delete from <%s>, ([0-9]*) \(or less\) triples -- done" % graph_uri
    not_found_message = "0 triples -- nothing to do"

    if re.search(delete_successful_message, query_result_message):
        return True
    elif re.search(not_found_message, query_result_message):
        return False
    else:
        raise UnexpectedResultException("Unknown result format: " + str(result_dict))


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
        if not is_reserved_attribute(predicate_uri):

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
                    object_value = escape_quotes(object_value)
                    object_ = '"%s"' % object_value
            triple = (instance, predicate, object_)
            triples.append(triple)

    return triples


ESCAPED_QUOTES = {
    u'"': u'\\"',
    u"'": u"\\'"
}


def escape_quotes(object_value):
    escaped_value = object_value
    for char in ESCAPED_QUOTES:
        escaped_value = escaped_value.replace(char, ESCAPED_QUOTES[char])

    return escaped_value


def create_implicit_triples(instance_uri, class_uri):
    class_triple = ("<%s>" % instance_uri, "a", "<%s>" % class_uri)
    return [class_triple]


TRIPLE = """   %s %s %s ."""


def join_triples(triples):
    triples_strings = [TRIPLE % triple for triple in triples]
    return "\n".join(triples_strings)


PREFIX = """PREFIX %s: <%s>"""


def join_prefixes(prefixes_dict):
    prefix_list = []
    for (slug, graph_uri) in prefixes_dict.items():
        if not slug.startswith("@"):
            prefix = PREFIX % (slug, graph_uri)
            prefix_list.append(prefix)
    return "\n".join(prefix_list)


QUERY_FILTER_LABEL_BY_LANGUAGE = """
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
        p_key = "p{0}".format(index)
        p_value = query_string_dict[p_key]
        o_key = "o{0}".format(index)
        o_value = query_string_dict[o_key]
        po_list.append((p_value, o_value, index))

    for index in only_p_is_defined:
        p_key = "p{0}".format(index)
        p_value = query_string_dict[p_key]
        o_value = "?o{0}".format(index)
        po_list.append((p_value, o_value, index))

    for index in only_o_is_defined:
        p_value = "?p{0}".format(index)
        o_key = "o{0}".format(index)
        o_value = query_string_dict[o_key]
        po_list.append((p_value, o_value, index))

    return sorted(po_list)
