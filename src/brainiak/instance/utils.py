from brainiak.utils.sparql import LABEL_PROPERTIES
from brainiak.prefixes import normalize_all_uris_recursively

def are_there_label_properties_in(instance_data):
    """
        Validate there are label properties in instance data when creating/modifying an instance
        LABEL_PROPERTIES is a list like [u'http://www.w3.org/2000/01/rdf-schema#label']
    """
    normalized_instance_data = normalize_all_uris_recursively(instance_data)
    for label_property in LABEL_PROPERTIES:
        if label_property in normalized_instance_data:
            return True
    return False
