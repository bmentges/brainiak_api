import urlparse
from math import ceil
from urllib import urlencode


def set_content_type_profile(handler, query_params):
    """Set header Content-Type + profile pointing to URL of the json-schema"""
    schema_url = build_schema_url(query_params)
    content_type = "application/json; profile={0}".format(schema_url)
    handler.set_header("Content-Type", content_type)


def assemble_url(url, params={}):
    url_parse = urlparse.urlparse(url)

    if isinstance(params, str):
        params = urlparse.parse_qs(params)

    if url_parse.query:
        existing_params = urlparse.parse_qs(url_parse.query)
        params = dict(params, **existing_params)
        url_size_minus_query_string = len(url_parse.query) + 1
        url = url[:-url_size_minus_query_string]

    if params:
        return "{0}?{1}".format(url, urlencode(params, doseq=True))
    else:
        return "{0}".format(url)


# TODO: refactor and add to a method similar to utils.params.args
def filter_query_string_by_key_prefix(query_string, include_prefixes=[]):
    query_string_dict = urlparse.parse_qs(query_string)
    relevant_params = {}
    for key, value in query_string_dict.items():
        if any([key.startswith(prefix) for prefix in include_prefixes]):
            relevant_params[key] = value
    return urlencode(relevant_params, doseq=True)


def remove_last_slash(url):
    return url[:-1] if url.endswith("/") else url


# def remove_class_slash(url):
#     url = url.replace('/_schema', '')
#     return url[:-1] if url.endswith("/") else url


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
            'href': "%s?%s" % (base_url, query_params.args(page=last_page, per_page=per_page)),
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
    """Add attributes and values related to pagination to a listing page"""
    page = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
    previous_page = get_previous_page(page)
    per_page = int(query_params["per_page"])
    result = {
        'page': page,
        'per_page': per_page
    }
    if previous_page:
        result['previous_page'] = previous_page

    if (query_params.get("do_item_count", None) == "1") and (total_items is not None):
        last_page = get_last_page(total_items, per_page)
    else:
        last_page = None
    next_page = get_next_page(page, last_page)
    if next_page:
        result['next_page'] = next_page

    if last_page:
        result['last_page'] = last_page

    return result


def pagination_schema(root_url):
    """Json schema part that expresses pagination structure"""
    def link(rel, href):
        link_pattern = {
            "href": href,
            "method": "GET",
            "rel": rel
        }
        return link_pattern

    result = {
        "properties": {
            "page": {"type": "integer", "minimum": 1},
            "per_page": {"type": "integer", "minimum": 1},
            "previous_page": {"type": "integer", "minimum": 1},
            "next_page": {"type": "integer"},
            "last_page": {"type": "integer"}
        },
        "links": [
            link('first', root_url + '?page=1&per_page={per_page}&do_item_count={do_item_count}'),
            link('previous', root_url + '?page={previous_page}&per_page={per_page}&do_item_count={do_item_count}'),
            link('next', root_url + '?page={next_page}&per_page={per_page}&do_item_count={do_item_count}'),
            link('last', root_url + '?page={last_page}&per_page={per_page}&do_item_count={do_item_count}')
        ]
    }
    return result


# TODO: deprecate this function
def collection_links(query_params):
    link_params = {}
    link_params['base_url'] = remove_last_slash(query_params.base_url)
    link_params['page'] = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
    link_params['per_page'] = int(query_params["per_page"])

    link_params['resource_url'] = remove_last_slash(query_params.resource_url)

    base_url = link_params['base_url']
    per_page = link_params['per_page']

    previous_page = get_previous_page(link_params['page'])
    next_page = get_next_page(link_params['page'])

    links = [
        {
            'rel': "first",
            'href': "%s?%s" % (base_url, query_params.args(page=1, per_page=per_page)),
            'method': "GET"
        },
    ]
    if previous_page:
        links.append({'rel': "previous",
                      'href': "%s?%s" % (base_url, query_params.args(page=previous_page, per_page=per_page)),
                      'method': "GET"})
    if next_page:
        links.append({'rel': "next",
                      'href': "%s?%s" % (base_url, query_params.args(page=next_page, per_page=per_page)),
                      'method': "GET"})
    return links


def build_class_url(query_params, include_query_string=False):
    class_url = "{0}://{1}/{2}/{3}".format(
        query_params['request'].protocol,
        query_params['request'].host,
        query_params['context_name'],
        query_params['class_name'])
    if include_query_string:
        query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"])
        class_url = assemble_url(class_url, query_string)
    return class_url


def build_schema_url(query_params):
    base_url = remove_last_slash(query_params.base_url)
    schema_url = assemble_url('{0}/_schema_list'.format(base_url))
    return schema_url


def build_schema_url_for_instance(query_params):
    class_url = build_class_url(query_params)
    query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"])
    schema_url = assemble_url('{0}/_schema'.format(class_url), query_string)
    return schema_url


def crud_links(query_params, schema_url=None):
    """Build crud links."""
    if schema_url is None:
        schema_url = build_schema_url_for_instance(query_params)

    class_url = build_class_url(query_params)
    querystring = query_params["request"].query
    if querystring:
        instance_url = "{0}/{1}?{2}".format(class_url, query_params["instance_id"], querystring)
    else:
        instance_url = "{0}/{1}".format(class_url, query_params["instance_id"])

    links = [
        {'rel': "delete", 'href': instance_url, 'method': "DELETE"},
        {'rel': "replace", 'href': instance_url, 'method': "PUT", 'schema': {'$ref': schema_url}}
    ]
    return links


def self_url(query_params):
    """Produce the url for the self link"""
    protocol = query_params['request'].protocol
    host = query_params['request'].host
    url = query_params['request'].uri
    if not host in url:
        url = "{0}://{1}{2}".format(protocol, host, url)
    return url


def add_link(link_list, rel, href, method='GET', **kw):
    "Add an entry to the list given by ``link_list'' with key==rel and href as a string template that is formated by kw"
    link = {'rel': rel, 'method': method, 'href': href}
    link.update(kw)
    link_list.append(link)


def status_link(query_params):
    """Build _status links"""
    protocol = query_params['request'].protocol
    host = query_params['request'].host
    url = "{0}://{1}/{2}".format(protocol, host, "_status")

    return [{"rel": "status", "href": url, "method": "GET"}]
