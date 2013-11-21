from urlparse import parse_qs, urlsplit, urlunsplit
from math import ceil
from urllib import urlencode, unquote


def split_prefix_and_id_from_uri(url):
    splitted_url = urlsplit(url)
    last_slash = splitted_url.path.rfind("/")
    id_ = splitted_url.path[last_slash + 1:]
    new_path = splitted_url.path[:last_slash + 1]
    prefix = urlunsplit([splitted_url.scheme, splitted_url.netloc, new_path, '', ''])
    return prefix, id_


def content_type_profile(schema_url):
    """Set header Content-Type + profile pointing to URL of the json-schema"""
    content_type = u"application/json; profile={0}".format(schema_url)
    return content_type


# todo: test
def merge_querystring(querystring, params):
    existing_params = parse_qs(querystring)
    params = dict(existing_params, **params)
    return unquote(urlencode(params, doseq=True))


# test: order between declarations in url and in params
def assemble_url(url="", params={}):
    splitted_url = urlsplit(url)

    if isinstance(params, str):
        params = parse_qs(params)

    query = merge_querystring(splitted_url.query, params)
    splitted_url = list(splitted_url)
    splitted_url[3] = query

    return urlunsplit(splitted_url)


# TODO: refactor and add to a method similar to utils.params.args
def filter_query_string_by_key_prefix(query_string, include_prefixes=[], query_params={}):
    query_string_dict = parse_qs(query_string)
    relevant_params = {}
    for key, value in query_string_dict.items():
        if any([key.startswith(prefix) for prefix in include_prefixes]):
            relevant_params[key] = value

    if query_params.get("context_name") == "_" and not "graph_uri" in relevant_params:
        relevant_params["graph_uri"] = query_params["graph_uri"]

    if query_params.get("class_name") == "_" and not "class_uri" in relevant_params:
        relevant_params["class_uri"] = query_params["class_uri"]

    return urlencode(relevant_params, doseq=True)


def remove_last_slash(url):
    if url.endswith("/"):
        return url[:-1]
    else:
        return url


def split_into_chunks(items, chunk_size):
    """
    Provided a list (items) and an integer representing the chunk size,
    creates a list of sub-lists (chunks) with size up to chunk_size.

    Useful for pagination.
    """
    chunks = [items[index: index + chunk_size] for index in xrange(0, len(items), chunk_size)]
    return chunks


def get_last_page(total_items, per_page):
    return int(ceil(total_items / float(per_page)))


def get_previous_page(page):
    if page > 1:
        return page - 1
    else:
        return False


def get_next_page(page, last_page=None):
    if last_page is not None:
        if page < last_page:
            return page + 1
        else:
            return False
    else:
        return page + 1


def last_link(query_params, total_items):
    link_params = {}
    link_params['base_url'] = remove_last_slash(query_params.base_url)
    link_params['page'] = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
    link_params['per_page'] = int(query_params["per_page"])
    base_url = link_params['base_url']
    per_page = link_params['per_page']
    last_page = get_last_page(total_items, link_params['per_page'])
    links = [
        {
            'rel': "last",
            'href': u"%s?%s" % (base_url, query_params.format_url_params(page=last_page, per_page=per_page)),
            'method': "GET"
        }
    ]
    return links


def merge_schemas(*dicts):
    "Merge the remaining json-schema dictionaries into the first"
    result = dicts[0]
    for d in dicts[1:]:
        result['properties'].update(d['properties'])
        result['links'].extend(d['links'])


def pagination_items(query_params, total_items=None):
    """Add attributes and values related to pagination to a listing page.
    See also https://coderwall.com/p/lkcaag?i=1&p=1&q=sort%3Aupvotes+desc&t[]=algorithm&t[]=algorithms
    """
    query_string = query_params["request"].query
    page = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
    per_page = int(query_params["per_page"])

    result = {
        "_first_args": merge_querystring(query_string, {"page": 1})
    }

    last_page = None
    if (query_params.get("do_item_count", None) == "1") and (total_items is not None):
        last_page = get_last_page(total_items, per_page)
        result["_last_args"] = merge_querystring(query_string, {"page": last_page})

    previous_page = get_previous_page(page)
    if previous_page:
        result["_previous_args"] = merge_querystring(query_string, {"page": previous_page})

    next_page = get_next_page(page, last_page)
    if next_page:
        result["_next_args"] = merge_querystring(query_string, {"page": next_page})

    return result


def pagination_schema(root_url, extra_url_params='', method="GET"):
    """Json schema part that expresses pagination structure"""
    def link(rel, href):
        link_pattern = {
            "href": href,
            "method": method,
            "rel": rel
        }
        return link_pattern

    result = {
        "properties": {
            "_first_args": {"type": "string"},
            "_previous_args": {"type": "string"},
            "_next_args": {"type": "string"},
            "_last_args": {"type": "string"},
        },
        "links": [
            link('first', '?{+_first_args}'),
            link('previous', '?{+_previous_args}'),
            link('next', '?{+_next_args}'),
            link('last', '?{+_last_args}')
        ]
    }
    return result


def build_relative_class_url(query_params, include_query_string=False):
    class_url = u"/{0}/{1}".format(
        query_params.get('context_name', '_'),
        query_params.get('class_name', '_'))
    if include_query_string:
        query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"])
        class_url = assemble_url(class_url, query_string)
    return class_url


def build_class_url(query_params, include_query_string=False):
    class_url = u"{0}://{1}/{2}/{3}".format(
        query_params['request'].protocol,
        query_params['request'].host,
        query_params.get('context_name', ''),
        query_params.get('class_name', ''))
    if include_query_string:
        query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"])
        class_url = assemble_url(class_url, query_string)
    return class_url


def build_schema_url(query_params):
    base_url = remove_last_slash(query_params.base_url)
    schema_url = assemble_url(u'{0}/_schema_list'.format(base_url))
    return schema_url


def build_schema_url_for_instance(query_params, class_url):
    query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"], query_params)
    schema_url = assemble_url(u'{0}/_schema'.format(class_url), query_string)
    return schema_url


def crud_links(query_params, class_url):
    """Build crud links."""
    querystring = query_params["request"].query
    if querystring:
        instance_url = u"{0}/{{_resource_id}}?instance_prefix={{_instance_prefix}}&{1}".format(class_url, querystring)
    else:
        instance_url = u"{0}/{{_resource_id}}".format(class_url)

    schema_url = build_schema_url_for_instance(query_params, class_url)
    links = [
        {'rel': "delete", 'href': instance_url, 'method': "DELETE"},
        {'rel': "update", 'href': instance_url, 'method': "PUT", 'schema': {'$ref': schema_url}}
    ]
    return links


def self_url(query_params):
    """Produce the url for the self link"""
    protocol = query_params['request'].protocol
    host = query_params['request'].host
    url = query_params['request'].uri
    if not host in url:
        url = u"{0}://{1}{2}".format(protocol, host, url)
    return url


def add_link(link_list, rel, href, method='GET', **kw):
    "Add an entry to the list given by ``link_list'' with key==rel and href as a string template that is formated by kw"
    link = {'rel': rel, 'method': method, 'href': href}
    link.update(kw)
    link_list.append(link)


# def collection_links(query_params):
#     link_params = {}
#     link_params['base_url'] = remove_last_slash(query_params.base_url)
#     link_params['page'] = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
#     link_params['per_page'] = int(query_params["per_page"])
#
#     link_params['resource_url'] = remove_last_slash(query_params.resource_url)
#
#     base_url = link_params['base_url']
#     per_page = link_params['per_page']
#
#     previous_page = get_previous_page(link_params['page'])
#     next_page = get_next_page(link_params['page'])
#
#     links = [
#         {
#             'rel': "first",
#             'href': "%s?%s" % (base_url, query_params.args(page=1, per_page=per_page)),
#             'method': "GET"
#         },
#     ]
#     if previous_page:
#         links.append({'rel': "previous",
#                       'href': "%s?%s" % (base_url, query_params.args(page=previous_page, per_page=per_page)),
#                       'method': "GET"})
#     if next_page:
#         links.append({'rel': "next",
#                       'href': "%s?%s" % (base_url, query_params.args(page=next_page, per_page=per_page)),
#                       'method': "GET"})
#     return links
