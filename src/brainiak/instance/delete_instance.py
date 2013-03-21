import json
from brainiak.utils.sparql import some_triples_deleted


def delete_instance(query_params):
    query_response = query_delete(query_params['graph_uri'],
                                  query_params['instance_uri'])

    query_result_dict = json.loads(query_response.body)

    if some_triples_deleted(query_result_dict):
        return True
    else:
        return False


def query_delete(graph_uri, instance_uri):
    pass
