# -*- coding: utf-8 -*-

from brainiak.triplestore import query_sparql


def query_class_schema(class_uri, callback):
    QUERY_TEMPLATE = """
        SELECT DISTINCT ?label ?comment
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?label . FILTER(langMatches(lang(?label), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri}
    # self.logger.info("%s" % QUERY_TEMPLATE)
    query_sparql(QUERY_TEMPLATE, callback)


def query_cardinalities(class_uri, callback):
    QUERY_TEMPLATE = u"""
    SELECT DISTINCT ?predicate ?min ?max ?range ?enumerated_value ?enumerated_value_label
    WHERE {
        <%(class_uri)s> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?s OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        ?s <http://www.w3.org/2002/07/owl#onProperty> ?predicate .
        OPTIONAL { ?s <http://www.w3.org/2002/07/owl#minQualifiedCardinality> ?min } .
        OPTIONAL { ?s <http://www.w3.org/2002/07/owl#maxQualifiedCardinality> ?max } .
        OPTIONAL {
          { ?s <http://www.w3.org/2002/07/owl#onClass> ?range }
          UNION { ?s <http://www.w3.org/2002/07/owl#onDataRange> ?range }
          UNION {
               ?s <http://www.w3.org/2002/07/owl#allValuesFrom> ?range  .
            }
            OPTIONAL { ?range owl:oneOf ?enumeration } .
            OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
            OPTIONAL { ?list_node rdf:first ?enumerated_value } .
            OPTIONAL { ?enumerated_value rdfs:label ?enumerated_value_label } .
        }
    }
    """ % {"class_uri": class_uri}
    # self.logger.info("%s" % str(QUERY))
    query_sparql(QUERY_TEMPLATE, callback)


def query_predicates(class_uri, callback):
    QUERY_TEMPLATE = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?label ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        <%(class_uri)s> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        GRAPH ?predicate_graph { ?predicate <http://www.w3.org/2000/01/rdf-schema#domain> ?domain_class  } .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#range> ?range .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#label> ?label .
        ?predicate <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        FILTER(langMatches(lang(?label), "%(lang)s")) .
        FILTER(langMatches(lang(?predicate_comment), "%(lang)s")) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range <http://www.w3.org/2000/01/rdf-schema#label> ?label_do_range . FILTER(langMatches(lang(?label_do_range), "%(lang)s")) . } } .
        OPTIONAL { ?predicate <http://www.w3.org/2000/01/rdf-schema#comment> ?predicate_comment }
    }""" % {'class_uri': class_uri, 'lang': 'PT'}

    def _response_handler(response):
        if not response['results']['bindings']:
            query_predicates_without_lang(class_uri, callback)
        else:
            callback(response)

    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(QUERY_TEMPLATE, _response_handler)


def query_predicates_without_lang(class_uri, callback):
    QUERY_TEMPLATE = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?label ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        <%(class_uri)s> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        GRAPH ?predicate_graph { ?predicate <http://www.w3.org/2000/01/rdf-schema#domain> ?domain_class  } .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#range> ?range .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#label> ?label .
        ?predicate <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range <http://www.w3.org/2000/01/rdf-schema#label> ?label_do_range . } } .
        OPTIONAL { ?predicate <http://www.w3.org/2000/01/rdf-schema#comment> ?predicate_comment }
    }""" % {'class_uri': class_uri}

    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(QUERY_TEMPLATE, callback)
