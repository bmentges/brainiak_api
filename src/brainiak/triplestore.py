from brainiak import settings

#def query_sparql(query):
#    """
#    Simple interface that given a SPARQL query string
#    returns a JSON SPARQL results bindings
#    """
#    connection = VirtuosoConnection()
#    return


SPARQL_RESULTS_FORMAT = "application/sparql-results+json"
URL_ENCODED = "application/x-www-form-urlencoded"


class VirtuosoConnection(object):

    def __init__(self):
        if hasattr(settings, "SPARQL_ENDPOINT_FULL_URL"):
            self.endpoint_url = settings.SPARQL_ENDPOINT_FULL_URL
        else:
            self.host = settings.SPARQL_ENDPOINT_HOST
            self.port = settings.SPARQL_ENDPOINT_PORT
            self.endpoint_url = self.host + ":" + str(self.port) + "/sparql"

#    def do_query(self, query):
#        pass
