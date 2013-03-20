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
        {
            'href': request_uri,
            'rel': "self"
        }
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

    navigation_links = [
        {
            'href': "%s?%s" % (class_uri, set_query_string_parameter(query_string, "page", "1")),
            'method': "GET",
            'rel': "first"
        },
        {
            'href': "%s?%s" % (class_uri, set_query_string_parameter(query_string, "page", last_page)),
            'method': "GET",
            'rel': "last"
        }
    ]

    previous_page = get_previous_page(page)
    if previous_page:
        item = {
            'href': "%s?%s" % (class_uri, set_query_string_parameter(query_string, "page", previous_page)),
            'method': "GET",
            'rel': "previous"
        }
        navigation_links.append(item)

    next_page = get_next_page(page, last_page)
    if next_page:
        item = {
            'href': "%s?%s" % (class_uri, set_query_string_parameter(query_string, "page", next_page)),
            'method': "GET",
            'rel': "next"
        }
        navigation_links.append(item)

    links.extend(navigation_links)

    return links
