from brainiak.stored_query import ES_INDEX_NAME, ES_TYPE_NAME
from brainiak.search_engine import get_all_instances_from_type



def get_stored_queries():
    queries = get_all_instances_from_type(ES_INDEX_NAME, ES_TYPE_NAME)
    if queries is None:
        # TODO 404
        pass
    else:
        # TODO 200
        # TODO get queries without ES metadata
        # TODO decorate with pagination
        return queries
