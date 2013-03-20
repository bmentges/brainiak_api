List of Instances
=================

This service retrieves all instances of a specific class or Instances
according a propert/value filter. The results are paginated.

Basic usage
------------

.. code-block:: http

  GET 'http://localhost:5100/place/Country'

This will retrieve all instances of ``Country`` in the place ``graph``

Optional parameters
-------------------

- lang: Specify language of labels. Options: pt, en, undefined (do not filter labels)
- graph_uri: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``
- class_uri: Set the class URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME``
- page: The page you want to retrieve. The default value is ``0``, i.e. the first page
- per_page: Defines how many items you want to retrieve per page. The default value is ``10``
- p: Filters the instances that have the (**p**)redicate specified used in a triple.
- o: Filters the instances that have the (**o**)bject specified used in a triple.

By combining ``p`` and ``o`` parameters you can specify a filter for instances that have
this property and object values. For exeample:

.. code-block:: http

  GET 'http://localhost:5100/place/Country?p=place:partOfContinent&?o=http://semantica.globo.com/place/Continent/America'

Possible responses
-------------------


Status 200
__________

If the instance exists, the response body is a JSON with all instance information and links to related actions.

.. include :: examples/get_instance_200.rst

Status 404
__________

If the instance does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_instance_404.rst

Status 400
__________

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/get_instance_400.rst
