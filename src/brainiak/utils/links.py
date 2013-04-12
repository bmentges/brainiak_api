from math import ceil


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


def collection_links(query_params, total_items):
    base_url = query_params.base_url
    page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
    per_page=int(query_params["per_page"])
    last_page = get_last_page(total_items, per_page)
    previous_page = get_previous_page(page)
    next_page = get_next_page(page, last_page)
    base_url_with_default_params = "{0}?{1:s}".format(base_url, query_params.args())
    class_url = "{0}/_schema?{1:s}".format(base_url, query_params.args())
    links = [
        {'rel': "create", 'href': base_url_with_default_params, 'method': "POST"},
        {'rel': "itemDescribedBy", 'href': class_url, 'method': "GET"},
        {'rel': "first", 'href': "%s?%s" % (base_url, query_params.args(page=1)), 'method': "GET"},
        {'rel': "last", 'href': "%s?%s" % (base_url, query_params.args(last_page=last_page)), 'method': "GET"}
    ]
    if previous_page:
        links.append({'rel': "previous", 'href': "%s?%s" % (base_url, query_params.args(page=previous_page)),
                          'method': "GET"})
    if next_page:
        links.append({'rel': "next", 'href': "%s?%s" % (base_url, query_params.args(page=next_page)),
                          'method': "GET"})
    return links


def crud_links(query_params):
    """Build crud links."""
    base_url = query_params.base_url
    resource_url = query_params.resource_url
    base_url_with_params = "{0}?{1:s}".format(base_url, query_params.args())
    links = [
        {'rel': "self", 'href': base_url_with_params},
        {'rel': "delete", 'href': resource_url, 'method': "DELETE"},
        {'rel': "replace", 'href': resource_url, 'method': "PUT"}
    ]
    return links


def add_link(link_list, rel, href, **kw):
    "Add an entry to the list given by ``link_list'' with key==rel and href as a string template that is formated by kw"
    link_list.append({'rel': rel, 'href': href.format(**kw)})
