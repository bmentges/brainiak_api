List of Instances
=================

This service retrieves all instances of a specific class or Instances
according a propert/value filter. The results are paginated.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/person/Gender/'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/person/Gender/' | python -mjson.tool
  :shell:

This will retrieve all instances of ``Gender`` in the graph ``person``

Optional parameters
-------------------

**lang**: Specify language of labels. Options: pt, en, undefined (do not filter labels)

**graph_uri**: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``

**class_uri**: Set the class URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME``

**page**: The page you want to retrieve. The default value is ``1``, i.e. the first page

**per_page**: Defines how many items you want to retrieve per page. The default value is ``10``

**p**: Filters the instances that have the (**p**)redicate specified used in a triple.

**o**: Filters the instances that have the (**o**)bject specified used in a triple.

**sort_by**: Defines predicate used to order instances. E.g: ``sort_by=rdfs:label`` or ``sort_by=dbpprop:stadium``.

**sort_order**: Defines if ordering will be ascending or descending. The default is ascending. E.g: ``sort_order=asc`` or ``sort_order=desc``.

By combining ``p`` and ``o`` parameters you can specify a filter for instances that have
this property and object values. For exeample:

.. code-block:: http

  GET 'http://localhost:5100/place/Country/?p=place:partOfContinent&?o=http://semantica.globo.com/place/Continent/America'

Possible responses
-------------------


**Status 200**

If there are instances that match the query, the response body is a JSON containing instances' titles, resources_id and @ids (URIs).
By default, the first page containing 10 items is returned (``?page=1&per_page=10``).

.. include :: examples/get_instance_200.rst

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. include :: examples/get_instance_400.rst

**Status 404**

If there are no instances, the response status code is a 404.

.. include :: examples/get_instance_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
