

def create_instance(query_params, instance_data):
    # create instance uri
    # parse tuples based on relevant data from query_params?
    # parse prefixes based on relevant data from query_params?
    # build insert query
    return "ok"


# TODO: test
PREFIX = """PREFIX %(slug)s: <%(graph_uri)s>"""


# TODO: test
TRIPLE = """   %(subject)s %(predicate)s %(object)s ."""


# TODO: test
QUERY_INSERT_TRIPLES = """
%(prefix)s
INSERT DATA INTO <%(graph_uri)s>
{
%(triples)s
}
"""
