from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.prefixes import prefix_to_slug, STANDARD_PREFIXES
from brainiak.utils import sparql
from brainiak.utils.decorator import memoize
from brainiak.utils.links import self_link, split_into_chunks, collection_links,\
    add_link, status_link

# Note that pagination was done outside the query
# because we are filtering query results based on prefixes
# (accessible from the application and not through SPARQL)

QUERY_LIST_CONTEXT = """
SELECT DISTINCT ?graph
WHERE {GRAPH ?graph { ?s a ?o }}
"""


@memoize
def list_all_contexts(params):
    sparql_response = triplestore.query_sparql(QUERY_LIST_CONTEXT)
    all_contexts_uris = sparql.filter_values(sparql_response, "graph")

    filtered_contexts = filter_and_build_contexts(all_contexts_uris)

    if not filtered_contexts:
        raise HTTPError(404, log_message="No contexts were found.")

    page_index = int(params["page"])
    per_page = int(params["per_page"])
    contexts_pages = split_into_chunks(filtered_contexts, per_page)
    contexts = contexts_pages[page_index]

    links = self_link(params) + collection_links(params) + status_link(params)
    add_link(links, "instances", params.base_url + "{resource_id}")

    json = {
        'items': contexts,
        'links': links
    }
    return json


def filter_and_build_contexts(contexts_uris):
    contexts = []
    for uri in contexts_uris:
        slug = prefix_to_slug(uri)
        # ignore standard graphs
        if slug in STANDARD_PREFIXES:
            continue
        if slug != uri:
            context_info = {
                "title": slug,
                "@id": uri
            }
            contexts.append(context_info)

    # decorate_with_resource_id
    for dict_item in contexts:
        dict_item['resource_id'] = dict_item['title']

    return contexts
