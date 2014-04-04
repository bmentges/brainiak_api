# -*- coding: utf-8 -*-
import ujson as json
import requests


def add_instance_with_url(url, data):
    """Use this method to add a Python dictionary given in data to the exact url given by ``url``
    """
    response = requests.put(url, data=json.dumps(data))
    return response.status_code, response.json()


def del_instance(url):
    "Delete the instance given by the param ``url``"
    response = requests.delete(url)
    return response.status_code, response.text


def extract_keys(list_of_dicts, key):
    """Given a list of dictionaries, this function generates a list of values,
    where each values is the whatever was associated with the given parameter ``key``
    in each dictionary of the input list.

    >>> extract_keys([{'a':1}, {'a':2}, {'a':3}], 'a')
    [1, 2, 3]
    """
    return [d[key] for d in list_of_dicts]


def fetch_page(url, headers={"Content-Type": "application/json"}):
    """
    Use requests module to fetch a page from the given ``url`.
    By default it sets parameter headers to {"Content-Type": "application/json"}.

    >>> fetch_page("http://localhost:5100")
    (200, {u'items': [{u'resource_id': u'owl#', u'@id': u'http://www.w3.org/2002/07/owl#', u'title': u'owl'},
                      {u'resource_id': u'person', u'@id': u'http://semantica.globo.com/person/', u'title': u'person'}],
           u'links': [{u'href': u'/', u'rel': u'self'}, {u'href': u'/', u'rel': u'list'}],
           u'item_count': 2})
    """
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()


def fetch_all_pages(url, update_key):
    """
    Fetch all pages starting from the given URL and extract the value associated to ``update_key``,
    using ``update+key`` as a dictionary key in each page response.

    >>> fetch_all_pages("http://localhost:5100", "items")
    [{u'resource_id': u'owl#', u'@id': u'http://www.w3.org/2002/07/owl#', u'title': u'owl'},
     {u'resource_id': u'person', u'@id': u'http://semantica.globo.com/person/', u'title': u'person'},
     {u'resource_id': u'', u'@id': u'http://semantica.globo.com/', u'title': u'glb'},
     {u'resource_id': u'ego', u'@id': u'http://semantica.globo.com/ego/', u'title': u'ego'},
     {u'resource_id': u'upper', u'@id': u'http://semantica.globo.com/upper/', u'title': u'upper'},
     {u'resource_id': u'esportes', u'@id': u'http://semantica.globo.com/esportes/', u'title': u'esportes'},
     {u'resource_id': u'place', u'@id': u'http://semantica.globo.com/place/', u'title': u'place'},
     {u'resource_id': u'organization', u'@id': u'http://semantica.globo.com/organization/', u'title': u'organization'},
     {u'resource_id': u'g1', u'@id': u'http://semantica.globo.com/G1/', u'title': u'g1'},
     {u'resource_id': u'tvg', u'@id': u'http://semantica.globo.com/tvg/', u'title': u'tvg'},
     {u'resource_id': u'eureka', u'@id': u'http://semantica.globo.com/eureka/', u'title': u'eureka'}]
    """
    response = []
    page_index = 1
    while True:
        status_code, partial_response = fetch_page(url + u"/?page={0}".format(page_index))
        if status_code == 200:
            response.extend(partial_response[update_key])
        else:
            raise Exception(u'Failed to fetch page with status code {0}'.format(status_code))
        if 'next' not in extract_keys(partial_response['links'], 'rel'):
            break  # this is the last page
        page_index += 1
    return response
