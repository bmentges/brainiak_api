from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.prefixes import prefix_to_slug
from brainiak.utils import sparql


QUERY_LIST_DOMAIN = """
SELECT DISTINCT ?graph
WHERE {GRAPH ?graph { ?s ?p ?o }}
LIMIT %(per_page)s
OFFSET %(page)s
"""


def list_domains(params):
    query = QUERY_LIST_DOMAIN % params
    sparql_response = triplestore.query_sparql(query)
    domains_uris = sparql.filter_values(sparql_response, "graph")
    if not domains_uris:
        raise HTTPError(404, log_message="No domains were found.")
    domains = build_domains(domains_uris)
    domains_json = build_json(domains)
    return domains_json


def build_domains(domains_uris):
    domains = []
    for uri in domains_uris:
        slug = prefix_to_slug(uri)
        if slug != uri:
            domain_info = {
                "title": slug,
                "@id": uri,
                "resource_id": slug
            }
            domains.append(domain_info)
    return domains


def build_json(domains):
    links = {}
    json = {
        'items': domains,
        'item_count': len(domains),
        'links': links
    }
    # TODO: add pagination
    return json
