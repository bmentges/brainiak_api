# -*- coding: utf-8 -*-
import json

from tornado import gen
from brainiak.settings import URI_PREFIX
from brainiak.triplestore import query_sparql
from brainiak.result_handler import is_result_empty


def get_instance(context_name, class_name, instance_id):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    query_response = query_all_properties_and_objects(context_name, class_name, instance_id)
    result_dict = json.loads(query_response.body)

    if is_result_empty(result_dict):
        return
    else:
        # TODO handling dict
        return result_dict


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = "SELECT ?p ?o {<%(prefix)s/%(context_name)s/%(class_name)s/%(instance_id)s> a <%(prefix)s/%(context_name)s/%(class_name)s>; ?p ?o}"


def query_all_properties_and_objects(context_name, class_name, instance_id):
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % {
        'instance_id': instance_id,
        'prefix': URI_PREFIX,
        'context_name': context_name,
        'class_name': class_name,
    }
    return query_sparql(query)
