# -*- coding: utf-8 -*-

"""
This module uses the following nomenclature:
 uri = http://a/b/cD
 prefix = http://a/b/c/ or http://a/b/c#
 item_ = D
 slug = x
 short_uri = x:D
"""

import re

from brainiak import settings


class InvalidModeForNormalizeUriError(Exception):
    pass

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
    "G1": "http://semantica.globo.com/G1/",
    "tvg": "http://semantica.globo.com/tvg/",
    "eureka": "http://semantica.globo.com/eureka/",
}

_MAP_SLUG_TO_PREFIX.update(STANDARD_PREFIXES)
_MAP_SLUG_TO_PREFIX.update(LOCAL_PREFIXES)
_MAP_SLUG_TO_PREFIX.update(LEGACY_PREFIXES)
_MAP_PREFIX_TO_SLUG = {v: k for k, v in _MAP_SLUG_TO_PREFIX.items()}


class PrefixError(Exception):
    pass


def prefix_from_uri(uri):
    return uri[:uri.rfind("/") + 1]


def safe_slug_to_prefix(prefix):
    return _MAP_SLUG_TO_PREFIX.get(prefix, prefix)


def slug_to_prefix(slug):
    try:
        prefix = _MAP_SLUG_TO_PREFIX[slug]
    except KeyError:
        raise PrefixError("Prefix is not defined for slug {0}".format(slug))
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
            return "{0}:{1}".format(prefix_to_slug(uri_prefix), item)
    else:
        return uri


def is_uri(something):
    if something.startswith("http://") or something.startswith("https://"):
        return True
    return False


def is_compressed_uri(candidate, extra_prefixes={}):
    if is_uri(candidate):
        return False
    try:
        slug, item_ = candidate.split(":")
    except ValueError:
        return False
    else:
        if _MAP_SLUG_TO_PREFIX.get(slug) or extra_prefixes.get(slug):
            return True
    return False


def expand_uri(short_uri):
    if is_uri(short_uri):
        return short_uri
    short_uri_pattern = re.compile(r"(\w+):(\S+)")
    match = short_uri_pattern.match(short_uri)
    if match:
        slug, item = match.groups()
        prefix = slug_to_prefix(slug)
        return "{0}{1}".format(prefix, item)
    else:
        return short_uri


UNDEFINED = None
SHORTEN = '0'
EXPAND = '1'


def normalize_uri(uri, mode):
    if mode == SHORTEN:
        return shorten_uri(uri)
    elif mode == EXPAND:
        return expand_uri(uri)
    raise InvalidModeForNormalizeUriError('Unrecognized mode {0:s}'.format(mode))


def get_prefixes_dict():
    return _MAP_SLUG_TO_PREFIX


class MemorizeContext(object):
    "Wrap operations replace_prefix() and uri_to_prefix() remembering all substitutions in the context attribute"
    def __init__(self, normalize_uri_mode=UNDEFINED):
        self._normalize_uri_mode = normalize_uri_mode
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

    # TODO: avoid duplication with normalize_uri function
    def normalize_uri(self, uri):
        if self._normalize_uri_mode == SHORTEN:
            return self.shorten_uri(uri)
        elif self._normalize_uri_mode == EXPAND:
            return expand_uri(uri)
        raise InvalidModeForNormalizeUriError('Unrecognized mode {0:s}'.format(self._normalize_uri_mode))


# TODO: verifify if module re would give better performance
# http://stackoverflow.com/questions/7539959/python-finding-whether-a-string-starts-with-one-of-a-lists-variable-length-pre
