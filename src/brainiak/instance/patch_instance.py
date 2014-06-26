from tornado.web import HTTPError

from brainiak.prefixes import normalize_all_uris_recursively


error_msg = u"Incorrect patch item. Every object in the list must contain the following keys: op, path and value"


def apply_patch(instance_data, patch_list):
    """
    Apply changes described in patch_list to the original instance_data.
    Return new dictionary containing the changes.
    
    For more information on patch_list: http://tools.ietf.org/html/rfc6902
    
    Example of usage:

    instance_data = {
        u'http://on.to/name': u'Flipper',
        u'http://on.to/age': 4
    }
    patch_list = [
        {
            u'path': u'http://on.to/age',
            u'value': 5,
            u'op': u'replace'
        }
    ]
    
    response = apply_patch(instance_data, patch_list)
    
    Value of response:
    
    reponse = {
        u'http://on.to/name': u'Flipper',
        u'http://on.to/age': 5
    }
    """

    patch_data = {}
    for item in patch_list:
        try:
            operation = item['op']
            predicate = item['path']
            value = item['value']
        except KeyError:
            raise HTTPError(400, log_message=error_msg)
            
        if operation == 'replace':
            patch_data[predicate] = value

    patch_data = normalize_all_uris_recursively(patch_data)
    changed_data = dict(instance_data, **patch_data)
    return changed_data
