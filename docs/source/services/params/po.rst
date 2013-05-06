
**p**: Filters the instances that have the (**p**)redicate specified used in a triple.

**o**: Filters the instances that have the (**o**)bject specified used in a triple.

By combining ``p`` and ``o`` parameters you can specify a filter for instances that have
this property and object values. For exeample:

.. code-block:: http

  GET 'http://api.semantica.dev.globoi.com/place/Country/?p=place:partOfContinent&o=http://semantica.globo.com/place/Continent/America'
