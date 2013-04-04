from math import ceil
from urllib import urlencode
from urlparse import parse_qs


def split_into_chunks(items, per_page):
    chunks = [items[index: index + per_page] for index in xrange(0, len(items), per_page)]
    return chunks


def set_query_string_parameter(query_string, param_name, param_value):
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    return new_query_string


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


def navigation_links(base_url, query_string, page, last_page):
    first_page_querystring = set_query_string_parameter(query_string, "page", "1")
    last_page_querystring = set_query_string_parameter(query_string, "page", last_page)
    nav_links = [
        {'rel': "first", 'href': "%s?%s" % (base_url, first_page_querystring), 'method': "GET"},
        {'rel': "last", 'href': "%s?%s" % (base_url, last_page_querystring), 'method': "GET"}
    ]

    previous_page = get_previous_page(page)
    if previous_page:
        previous_page_querystring = set_query_string_parameter(query_string, "page", previous_page)
        item = {'rel': "previous", 'href': "%s?%s" % (base_url, previous_page_querystring), 'method': "GET"}
        nav_links.append(item)

    next_page = get_next_page(page, last_page)
    if next_page:
        next_page_querystring = set_query_string_parameter(query_string, "page", next_page)
        item = {'rel': "next", 'href': "%s?%s" % (base_url, next_page_querystring), 'method': "GET"}
        nav_links.append(item)
    return nav_links


def build_links(base_url, page, per_page, request_url, total_items, query_string):
    """
    Build links for listing primitives (list contexts, list classes, list instances).
     - base_url: last character shouldn't be "/"
    """
    last_page = get_last_page(total_items, per_page)

    if base_url.endswith("/"):
        resource_url = "%s{resource_id}" % base_url
    else:
        resource_url = "%s/{resource_id}" % base_url

    links = [
        {'rel': "self", 'href': request_url}
    ]

    action_links = [
        {'rel': "list", 'href': base_url},
        {'rel': "item", 'href': resource_url},
        {'rel': "create", 'href': base_url, 'method': "POST"},
        {'rel': "delete", 'href': resource_url, 'method': "DELETE"},
        {'rel': "replace", 'href': resource_url, 'method': "PUT"}
    ]
    links.extend(action_links)

    nav_links = navigation_links(base_url, query_string, page, last_page)
    links.extend(nav_links)

    return links
