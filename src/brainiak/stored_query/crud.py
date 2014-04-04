from brainiak.search_engine import save_instance

ES_INDEX_NAME = "brainiak"
ES_TYPE_NAME = "query"

def store_query(entry, query_id):
    save_instance(entry, ES_INDEX_NAME, ES_TYPE_NAME, query_id)
