# -*- coding: utf-8 -*-

# """
# This module uses the following nomenclature:
#  uri = http://a/b/cD
#  prefix = http://a/b/c/ or http://a/b/c#
#  item_ = D
#  slug = x
#  short_uri = x:D
# """

from brainiak import settings


class InvalidModeForNormalizeUriError(Exception):
    pass

# URI Normalization operation modes
UNDEFINED = None
SHORTEN = '0'
EXPAND = '1'


# This ROOT CONTEXT is a special context whose URI is equal to the settings.URL_PREFIX
ROOT_CONTEXT = 'glb'

# Maps prefix_slug (key) -> prefix (value)
_MAP_SLUG_TO_PREFIX = {}

STANDARD_PREFIXES = {
    'nodeID': 'nodeID',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
}

LOCAL_PREFIXES = {
    'schema': 'http://schema.org/',
    'dbpedia': 'http://dbpedia.org/ontology/',
    'time': 'http://www.w3.org/2006/time#',
    'event': 'http://purl.org/NET/c4dm/event.owl#',
    'upper': 'http://semantica.globo.com/upper/',
    'place': 'http://semantica.globo.com/place/',
    'person': 'http://semantica.globo.com/person/',
    'organization': 'http://semantica.globo.com/organization/'
}

LEGACY_PREFIXES = {
    ROOT_CONTEXT: settings.URI_PREFIX,
    "base": "http://semantica.globo.com/base/",
    "ego": "http://semantica.globo.com/ego/",
    "esportes": "http://semantica.globo.com/esportes/",
    "g1": "http://semantica.globo.com/G1/",
    "tvg": "http://semantica.globo.com/tvg/",
    "eureka": "http://semantica.globo.com/eureka/",
    "tecnologia": "http://semantica.globo.com/tecnologia/",
    "techtudo": "http://semantica.globo.com/techtudo/"
}

_MAP_SLUG_TO_PREFIX.update(STANDARD_PREFIXES)
_MAP_SLUG_TO_PREFIX.update(LOCAL_PREFIXES)
_MAP_SLUG_TO_PREFIX.update(LEGACY_PREFIXES)
_MAP_PREFIX_TO_SLUG = {v: k for k, v in _MAP_SLUG_TO_PREFIX.items()}


class PrefixError(Exception):
    pass


def list_prefixes():
    prefixes_dict = get_prefixes_dict()
    result_dict = dict([("@context", prefixes_dict), ("root_context", ROOT_CONTEXT)])
    return result_dict


def prefix_from_uri(uri):
    return uri[:uri.rfind("/") + 1]


def safe_slug_to_prefix(prefix):
    return _MAP_SLUG_TO_PREFIX.get(prefix, prefix)


def slug_to_prefix(slug, translation_map=_MAP_SLUG_TO_PREFIX):
    try:
        prefix = translation_map[slug]
    except KeyError:
        raise PrefixError(u"Prefix is not defined for slug {0}".format(slug))
    return prefix


def prefix_to_slug(prefix):
    return _MAP_PREFIX_TO_SLUG.get(prefix, prefix)


def uri_to_slug(uri):
    return _MAP_PREFIX_TO_SLUG.get(extract_prefix(uri), uri)


def extract_prefix(uri):
    prefixes = _MAP_PREFIX_TO_SLUG.keys()
    # FIXME: Optmize way the two operations below
    prefixes.sort()
    prefixes.reverse()
    # Inspired by code from Vaughn Cato
    uri_prefix = filter(uri.startswith, prefixes + [''])[0]
    return uri_prefix


def shorten_uri(uri):
    uri_prefix = extract_prefix(uri)
    if uri_prefix:
        item = uri[len(uri_prefix):]
        if "/" in item:
            # compression was not perfect because the uri is longer than just slug:item
            return uri
        else:
            if not item:
                return u"{0}".format(prefix_to_slug(uri_prefix))
            else:
                return u"{0}:{1}".format(prefix_to_slug(uri_prefix), item)
    else:
        return uri


def is_uri(something):
    if (something is not None) and (isinstance(something, basestring)) and \
       (something.startswith("http://") or something.startswith("https://")):
            return True
    return False


def is_compressed_uri(candidate, extra_prefixes=None):
    if not isinstance(candidate, basestring) or is_uri(candidate):
        return False
    try:
        slug, item_ = candidate.split(":")
    except ValueError:
        return False
    else:
        if _MAP_SLUG_TO_PREFIX.get(slug) or (extra_prefixes and extra_prefixes.get(slug)):
            return True
    return False


def expand_uri(short_uri, translation_map=_MAP_SLUG_TO_PREFIX, context=None):
    if short_uri is None:
        return ''
    if is_uri(short_uri):
        return short_uri
    try:
        slug, item = short_uri.split(":")
    except ValueError:
        return short_uri

    local_map = {}
    if translation_map is not None:
        local_map.update(translation_map)
    if context is not None:
        local_map.update(context)

    if slug not in local_map:
        return short_uri

    prefix = slug_to_prefix(slug, local_map)

    return u"{0}{1}".format(prefix, item)


def normalize_uri(uri, mode, shorten_uri_function=shorten_uri, context=None):
    if mode == SHORTEN:
        return shorten_uri_function(uri)
    elif mode == EXPAND:
        return expand_uri(uri, context=context)
    raise InvalidModeForNormalizeUriError(u'Unrecognized mode {0:s}'.format(mode))


def normalize_all_uris_recursively(instance, mode=EXPAND, context=_MAP_SLUG_TO_PREFIX):
    if isinstance(instance, basestring):
        try:
            response = normalize_uri(instance, mode, context=context)
        except PrefixError:
            response = instance
        return response
    elif isinstance(instance, list):
        return [normalize_all_uris_recursively(i, mode, context) for i in instance]
    elif isinstance(instance, dict):
        if '@context' in instance:
            new_ctx = {}
            new_ctx.update(instance['@context'])
            new_ctx.update(context)
        else:
            new_ctx = context
        response = {normalize_all_uris_recursively(k, mode, new_ctx): normalize_all_uris_recursively(v, mode, new_ctx)
                    for (k, v) in instance.items()}

        # Clean-up context only preserving @language -- FIXME: FRAGILE
        if mode == EXPAND and '@context' in response:
            lang = response['@context'].get('@language', None)
            if lang:
                response['@context'] = {'@language': lang}
            else:
                del response['@context']
        return response

    return instance


def get_prefixes_dict():
    return _MAP_SLUG_TO_PREFIX


class MemorizeContext(object):
    """Wrap operations replace_prefix() and uri_to_prefix() remembering all substitutions in the context attribute.
    Remember how to handle URI normalization preferences."""
    def __init__(self, normalize_uri=UNDEFINED):
        self._normalize_uri = normalize_uri
        self.context = {}
        self.object_properties = {}

    def add_object_property(self, property_name, uri):
        self.object_properties[shorten_uri(property_name)] = shorten_uri(uri)

    def shorten_uri(self, uri):
        short_uri = shorten_uri(uri)
        if short_uri != uri:
            self.context[uri_to_slug(uri)] = extract_prefix(uri)
        return short_uri

    def prefix_to_slug(self, prefix):
        slug = prefix_to_slug(prefix)
        if slug != prefix:
            self.context[slug] = prefix
        return slug

    def normalize_prefix_value(self, slug_or_uri):
        if self._normalize_uri == SHORTEN:
            return self.prefix_to_slug(slug_or_uri)
        elif self._normalize_uri == EXPAND:
            return safe_slug_to_prefix(slug_or_uri)
        raise InvalidModeForNormalizeUriError(u'Unrecognized mode {0:s}'.format(self._normalize_uri))

    def normalize_uri(self, uri):
        return normalize_uri(uri, self._normalize_uri, shorten_uri_function=self.shorten_uri)

# TODO: verifify if module re would give better performance
# http://stackoverflow.com/questions/7539959/python-finding-whether-a-string-starts-with-one-of-a-lists-variable-length-pre
