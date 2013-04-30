from math import ceil
from urllib import urlencode
import urlparse


def assemble_url(url, params={}):
    url_parse = urlparse.urlparse(url)

    if url_parse.query:
        existing_params = urlparse.parse_qs(url_parse.query)
        params = dict(params, **existing_params)
        url_size_minus_query_string = len(url_parse.query) + 1
        url = url[:-url_size_minus_query_string]

    if params:
        if isinstance(params, str):
            params = urlparse.parse_qs(params)
        return "{0}?{1}".format(url, urlencode(params, doseq=True))
    else:
        return "{0}".format(url)


def filter_query_string_by_key_prefix(query_string, prefixes=["class", "graph"]):
    query_string_dict = urlparse.parse_qs(query_string)
    relevant_params = {}
    for key, value in query_string_dict.items():
        if any([key.startswith(prefix) for prefix in prefixes]):
            relevant_params[key] = value
    return urlencode(relevant_params, doseq=True)


def remove_last_slash(url):
    return url[:-1] if url.endswith("/") else url


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


def get_next_page(page, last_page):
    if page < last_page:
        return page + 1
    else:
        return False


def prepare_link_params(query_params):
    "Utility function shared amongst assemble link functions that sets some reused params"
    link_params = {}
    link_params['base_url'] = remove_last_slash(query_params.base_url)
    try:
        link_params['page'] = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
        link_params['per_page'] = int(query_params["per_page"])
    except KeyError:
        pass
    link_params['resource_url'] = remove_last_slash(query_params.resource_url)

    if 'page' in query_params['request'].arguments:
        link_params['args'] = query_params.args(page=link_params['page'], per_page=link_params['per_page'])
    else:
        link_params['args'] = query_params.args()

    if link_params['args']:
        link_params['base_url_with_params'] = "{0}?{1:s}".format(link_params['base_url'], link_params['args'])
    else:
        link_params['base_url_with_params'] = remove_last_slash(link_params['base_url'])

    return link_params


def collection_links(query_params, total_items):

    link_params = prepare_link_params(query_params)
    base_url = link_params['base_url']
    per_page = link_params['per_page']

    last_page = get_last_page(total_items, link_params['per_page'])
    previous_page = get_previous_page(link_params['page'])
    next_page = get_next_page(link_params['page'], last_page)

    links = [
        {'rel': "first", 'href': "%s?%s" % (base_url, query_params.args(page=1, per_page=per_page)), 'method': "GET"},
        {'rel': "last", 'href': "%s?%s" % (base_url, query_params.args(page=last_page, per_page=per_page)), 'method': "GET"}
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


def crud_links(query_params):
    """Build crud links."""
    schema_url = "{0}://{1}/{2}/{3}/_schema".format(
        query_params['request'].protocol,
        query_params['request'].host,
        query_params['context_name'],
        query_params['class_name'])

    link_params = prepare_link_params(query_params)
    links = [
        {'rel': "delete", 'href': link_params['base_url_with_params'], 'method': "DELETE"},
        {'rel': "replace", 'href': link_params['base_url_with_params'], 'method': "PUT", 'schema': {'$ref': schema_url}}
    ]
    return links


def self_link(query_params):
    "Produce a list with a single 'self' link entry"
    link_params = prepare_link_params(query_params)
    return [{'rel': "self", 'href': link_params['base_url_with_params'], 'method': "GET"}]


def add_link(link_list, rel, href, method='GET', **kw):
    "Add an entry to the list given by ``link_list'' with key==rel and href as a string template that is formated by kw"
    link = {'rel': rel, 'method': method, 'href': href}
    link.update(kw)
    link_list.append(link)
