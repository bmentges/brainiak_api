
**expand_uri**: The URIs that represent ``names`` and  ``values`` of properties in the response are either compressed (0) or expanded (1) by this parameter.

By default, this parameter is set to 0, meaning that URIs are compressed for keys and values.

This is going to change in future versions, and the default will be URI expansion.
So, we ask you to use this parameter explicitly and not rely on the default behaviour.

For example, ``rdfs:label`` is the compressed form, while ``http://www.w3.org/2000/01/rdf-schema#label`` is the respective expanded form.
