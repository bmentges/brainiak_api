from math import ceil


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


def collection_links(query_params, total_items):
    base_url = remove_last_slash(query_params.base_url)
    page = int(query_params["page"]) + 1  # Params class subtracts 1 from given param
    per_page = int(query_params["per_page"])
    last_page = get_last_page(total_items, per_page)
    previous_page = get_previous_page(page)
    next_page = get_next_page(page, last_page)
    args = query_params.args()
    if args:
        base_url_with_default_params = "{0}?{1:s}".format(base_url, args)
        #class_url = "{0}/_schema?{1:s}".format(base_url, args)
        item_url = "{0}/{{resource_id}}?{1:s}".format(base_url, args)
    else:
        base_url_with_default_params = base_url
        #class_url = "{0}/_schema".format(base_url)
        item_url = "{0}/{{resource_id}}".format(base_url)
    links = [
        {'rel': "create", 'href': base_url_with_default_params, 'method': "POST"},
        {'rel': "item", 'href': item_url, 'method': "GET"},
        #{'rel': "itemDescribedBy", 'href': class_url, 'method': "GET"},
        {'rel': "first", 'href': "%s?%s" % (base_url, query_params.args(page=1)), 'method': "GET"},
        {'rel': "last", 'href': "%s?%s" % (base_url, query_params.args(page=last_page)), 'method': "GET"}
    ]
    if previous_page:
        links.append({'rel': "previous",
                      'href': "%s?%s" % (base_url, query_params.args(page=previous_page)),
                      'method': "GET"})
    if next_page:
        links.append({'rel': "next",
                      'href': "%s?%s" % (base_url, query_params.args(page=next_page)),
                      'method': "GET"})
    return links


def crud_links(query_params):
    """Build crud links."""
    base_url = query_params.base_url
    resource_url = remove_last_slash(query_params.resource_url)
    args = query_params.args()
    if args:
        base_url_with_params = "{0}?{1:s}".format(base_url, args)
    else:
        base_url_with_params = remove_last_slash(base_url)
    links = [
        {'rel': "self", 'href': base_url_with_params, 'method': "GET"},
        {'rel': "delete", 'href': resource_url, 'method': "DELETE"},
        {'rel': "replace", 'href': resource_url, 'method': "PUT"}
    ]
    return links


def add_link(link_list, rel, href, method='GET', **kw):
    "Add an entry to the list given by ``link_list'' with key==rel and href as a string template that is formated by kw"
    link_list.append({'rel': rel, 'method': method, 'href': href.format(**kw)})
