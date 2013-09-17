
**expand_uri_keys**: The URIs that represent ``names`` of properties in the response are either compressed (0) or expanded (1) by this parameter.

**expand_uri_values**: The URIs that represent ``values`` of properties in the response are either compressed (0) or expanded (1) by this parameter.

**expand_uri**: This parameter sets simultaneously the parameters ``expand_uri_keys`` and ``expand_uri_values``

By default, this parameter is set to 0, meaning that URIs are compressed for keys and values.

For example, ``rdfs:label`` is the compressed form, while ``http://www.w3.org/2000/01/rdf-schema#label`` is the respective expanded form.
