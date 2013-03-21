from math import ceil
from urllib import urlencode
from urlparse import parse_qs


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


def build_links(class_uri, page, per_page, request_uri, total_items, query_string):
    last_page = get_last_page(total_items, per_page)
    resource_uri = "%s/{resource_id}" % class_uri

    links = [
        {'rel': "self", 'href': request_uri}
    ]

    action_links = [
        {'rel': "list", 'href': class_uri},
        {'rel': "item", 'href': resource_uri},
        {'rel': "create", 'href': class_uri, 'method': "POST"},
        {'rel': "delete", 'href': resource_uri, 'method': "DELETE"},
        {'rel': "edit", 'href': resource_uri, 'method': "PATCH"},
        {'rel': "replace", 'href': resource_uri, 'method': "PUT"}
    ]
    links.extend(action_links)

    first_page_querystring = set_query_string_parameter(query_string, "page", "1")
    last_page_querystring = set_query_string_parameter(query_string, "page", last_page)
    navigation_links = [
        {'rel': "first", 'href': "%s?%s" % (class_uri, first_page_querystring), 'method': "GET"},
        {'rel': "last", 'href': "%s?%s" % (class_uri, last_page_querystring), 'method': "GET"}
    ]

    previous_page = get_previous_page(page)
    if previous_page:
        previous_page_querystring = set_query_string_parameter(query_string, "page", previous_page)
        item = {'rel': "previous", 'href': "%s?%s" % (class_uri, previous_page_querystring), 'method': "GET"}
        navigation_links.append(item)

    next_page = get_next_page(page, last_page)
    if next_page:
        next_page_querystring = set_query_string_parameter(query_string, "page", next_page)
        item = {'rel': "next", 'href': "%s?%s" % (class_uri, next_page_querystring), 'method': "GET"}
        navigation_links.append(item)

    links.extend(navigation_links)

    return links
