# # -*- coding: utf-8 -*-
# from tornado import gen
# from brainiak.settings import URI_PREFIX
# from brainiak.triplestore import query_sparql


# @gen.engine
# def get_instance(context_name, class_name, instance_id, callback):
#     """
#     Given a URI, verify that the type corresponds to the class being passed as a parameter
#     Retrieve all properties and objects of this URI (subject)
#     """
#     # TODO verify app-semantica query
#     QUERY_TEMPLATE = """SELECT * { <%(instance_id)s> a <%(prefix)s/%(context_name)s/%(class_name)s> ; ?p ?o}
#     }""" % {'context_name': context_name, 'class_name': class_name, 'prefix': URI_PREFIX}
#     # self.logger.info(QUERY_TEMPLATE)
#     response = gen.Task(query_sparql, QUERY_TEMPLATE)
#     return response.body
