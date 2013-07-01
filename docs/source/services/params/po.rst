
**p**: Filters the instances that have the (**p**)redicate specified used in a triple.

**o**: Filters the instances that have the (**o**)bject specified used in a triple.

By combining ``p`` and/or ``o`` parameters you can specify a filter for instances that have
this property and/or object values. For example:

.. code-block:: http

  GET 'http://api.semantica.dev.globoi.com/place/Country/?p=place:partOfContinent&o=http://semantica.globo.com/place/Continent/America'

It is possible to use multiple ``p's`` and ``o's``, adding a number after them (p1, o1, p2, o2, etc). Example:

.. code-block:: http

  GET 'http://api.semantica.dev.globoi.com/place/City/?o=base:UF_RJ&p1=place:longitude&p2=place:latitude'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/City/?o=base:UF_RJ&p1=place:longitude&p2=place:latitude' | python -mjson.tool
  :shell:




