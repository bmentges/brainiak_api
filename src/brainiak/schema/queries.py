QUERY_CARDINALITIES = """
SELECT DISTINCT ?predicate ?min ?max ?range ?enumerated_value ?enumerated_value_label
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> rdfs:subClassOf ?s OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
    ?s owl:onProperty ?predicate .
    OPTIONAL { ?s owl:minQualifiedCardinality ?min } .
    OPTIONAL { ?s owl:maxQualifiedCardinality ?max } .
    OPTIONAL {
        { ?s owl:onClass ?range }
        UNION { ?s owl:onDataRange ?range }
        UNION { ?s owl:allValuesFrom ?range }
        OPTIONAL { ?range owl:oneOf ?enumeration } .
        OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
        OPTIONAL { ?list_node rdf:first ?enumerated_value } .
        OPTIONAL { ?enumerated_value rdfs:label ?enumerated_value_label } .
    }
}"""

QUERY_CLASS_SCHEMA = """
SELECT DISTINCT ?title ?comment
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> a owl:Class .
    {<%(class_uri)s> rdfs:label ?title . FILTER(langMatches(lang(?title), "PT")) . }
    {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
}
"""

QUERY_PREDICATES_WITH_LANG = """
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
    GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
    ?predicate rdfs:range ?range .
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
    FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
    FILTER(langMatches(lang(?title), "%(lang)s")) .
    FILTER(langMatches(lang(?predicate_comment), "%(lang)s")) .
    OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . FILTER(langMatches(lang(?label_do_range), "%(lang)s")) . } } .
    OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
}"""

QUERY_PREDICATES_WITHOUT_LANG = """
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
    GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
    ?predicate rdfs:range ?range .
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
    FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
    OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . } } .
    OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
}"""
