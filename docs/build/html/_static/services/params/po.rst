
**p**: Filters the instances that have the (**p**)redicate specified used in a triple.

**o**: Filters the instances that have the (**o**)bject specified used in a triple.

By combining ``p`` and/or ``o`` parameters you can specify a filter for instances that have
this property and/or object values. For example:

.. code-block:: http

  GET 'http://brainiak.semantica.dev.globoi.com/place/Country/?p=place:partOfContinent&o=http://semantica.globo.com/place/Continent/America'

It is also possible to set multiple ``p's`` and/or ``o's``, adding a number after them (p1, o1, p2, o2, etc). Example:

.. code-block:: http

  GET 'http://brainiak.semantica.dev.globoi.com/place/City/?o=base:UF_RJ&p1=place:longitude&p2=place:latitude&per_page=1''

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/City/?o=base:UF_RJ&p1=place:longitude&p2=place:latitude&per_page=1' | python -mjson.tool
  :shell:

Note by this last example that if only the predicate is provided, the related object for each item will be returned.
In this case, the key will be the shorten URI of the predicate and the object will be the items' objects.
From the example: ``place:longitude: "-43.407133"``

The same stands if only the object is provided, the predicate will be returned.
In this case, the key will be the query string's predicate label (eg: p, p1, p2, ..) and the value will be the predicate itself.
From the example above: ``p: "http://purl.org/dc/terms/isPartOf"``.





