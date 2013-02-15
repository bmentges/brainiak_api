from brainiak.server import settings

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
        if not settings.SPARQL_ENDPOINT_FULL_URL:
            self.host = settings.SPARQL_ENDPOINT_HOST
            self.port = settings.SPARQL_ENDPOINT_PORT
            self.endpoint_url = self.host + ":" + self.port + "/sparql"
        else:
            self.endpoint_url = settings.SPARQL_ENDPOINT_FULL_URL

        if settings.SPARQL_ENDPOINT_HTTP_METHOD:
            self.http_method = settings.SPARQL_ENDPOINT_HTTP_METHOD
        else:
            self.http_method = "POST"

    def do_query(self, query):
        pass
