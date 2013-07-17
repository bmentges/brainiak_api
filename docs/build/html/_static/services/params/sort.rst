**sort_by**: Defines predicate used to order instances. The sorting can also behave as a **p** filter, read **sort_include_empty**. Usage: ``sort_by=rdfs:label`` or ``sort_by=dbprop:stadium``.

**sort_order**: Defines if ordering will be ascending or descending. The default is ascending. E.g: ``sort_order=asc`` or ``sort_order=desc``.

**sort_include_empty**: By default, items that don't define **sort_by** property are also listed (``sort_include_empty=1``). If it is desired to exclude such items, set ``sort_include_empty=0``.
