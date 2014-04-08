from brainiak.search_engine import save_instance, get_instance,\
    delete_instance

ES_INDEX_NAME = "brainiak"
ES_TYPE_NAME = "query"


def store_query(entry, query_id):
    if stored_query_exists(query_id):
        save_instance(entry, ES_INDEX_NAME, ES_TYPE_NAME, query_id)
        return 200
    else:
        save_instance(entry, ES_INDEX_NAME, ES_TYPE_NAME, query_id)
        return 201


def get_stored_query(query_id):
    instance = get_instance(ES_INDEX_NAME, ES_TYPE_NAME, query_id)
    if instance is not None:
        return instance["_source"]


def stored_query_exists(query_id):
    return get_stored_query(query_id) is not None


def delete_stored_query(query_id):
    return delete_instance(ES_INDEX_NAME, ES_TYPE_NAME, query_id)
