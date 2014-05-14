**page**: The page to be retrieved. The default value is ``1``, i.e. the first page.

**per_page**: Defines how many items are retrieved per page. The default value is ``10``

 By default, the first page containing 10 items is returned. It could also be retrieved by:

.. code-block:: http

  GET 'http://brainiak.semantica.dev.globoi.com/?page=1&per_page=10'
