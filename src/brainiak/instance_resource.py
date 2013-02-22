# -*- coding: utf-8 -*-
from tornado import gen
from brainiak.settings import URI_PREFIX
from brainiak.triplestore import query_sparql


@gen.engine
def get_instance(context_name, schema_name, callback):
    QUERY_TEMPLATE = """SELECT * { ?s a  <%(prefix)s/%(context_name)s/%(schema_name)s> }
    }""" % {'context_name': context_name, 'schema_name': schema_name, 'prefix': URI_PREFIX}
    # self.logger.info(QUERY_TEMPLATE)
    response = gen.Task(query_sparql, QUERY_TEMPLATE)
    return response.body
