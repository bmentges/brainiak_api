# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, RequestHandler


class SchemaResource(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaResource, self).__init__(*args, **kwargs)

    # @asynchronous
    # @gen.engine
    # def post(self, context_name, collection_name, schema_name):
    #     #data = yield gen.Task(self._entities.add, context_name, collection_name, self.request.body)
    #     self.set_status(201)
    #     #self.set_header('Location', headers.location(self.request, data['slug']))
    #     self.finish()

    @asynchronous
    @gen.engine
    def get(self, context_name, schema_name):
        #data = yield gen.Task(self._entities.paginate, context_name, collection_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write('')
        self.finish()


"""
Consultas que retornam definição de uma classe

SELECT DISTINCT ?label ?comment WHERE {
          <http://semantica.globo.com/person/Person> a owl:Class .
          {<http://semantica.globo.com/person/Person> rdfs:label ?label . FILTER(langMatches(lang(?label), "PT")) . }
          {<http://semantica.globo.com/person/Person> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
}


SELECT DISTINCT ?predicate ?min ?max ?range ?enumerated_value ?enumerated_value_label WHERE {
        <http://semantica.globo.com/person/Person> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?s OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
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

SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?label ?grafo_do_range ?label_do_range ?super_property  WHERE {
        <http://semantica.globo.com/person/Person> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        GRAPH ?predicate_graph { ?predicate <http://www.w3.org/2000/01/rdf-schema#domain> ?domain_class  } .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#range> ?range .
        ?predicate <http://www.w3.org/2000/01/rdf-schema#label> ?label .
        ?predicate <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        FILTER(langMatches(lang(?label), "PT")) .
        FILTER(langMatches(lang(?predicate_comment), "PT")) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range <http://www.w3.org/2000/01/rdf-schema#label> ?label_do_range . FILTER(langMatches(lang(?label_do_range), "PT")) . } } .
        OPTIONAL { ?predicate <http://www.w3.org/2000/01/rdf-schema#comment> ?predicate_comment }

}
"""
