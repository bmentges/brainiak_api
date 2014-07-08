# coding: utf-8

PREDICATE_DICT_ORIGINAL = {
    "class": "c",
    "graph": "g",
    "predicates": {
        "p1": {
            "label": "l1",
            "graph": "g1",
            "type": "t1",
            "range": {
                "ra": {
                    "label": "la",
                    "graph": "ga"
                },
                "rb": {
                    "label": "lb",
                    "graph": "gb"
                },
                "rc": {
                    "label": "lc",
                    "graph": "ga"
                },
            },
            "subproperty": {}
        },
        "p2": {
            "label": "l2",
            "graph": "g2",
            "type": "t2",
            "range": {
                "oi": {}
            }
        }
    }
}

RANGES_DICT = {
    "ra": {
        "label": "la",
        "graph": "ga"
    },
    "rb": {
        "label": "lb",
        "graph": "gb"
    },
    "rc": {
        "label": "lc",
        "graph": "ga"
    },
}

EMPTY_GRAPHS_RANGES_DICT = {
    "oi": {},
    "outro_range": {}
}


SIMPLIFIED_PREDICATE_DICT = {
    "p1": {
        'ranges': ['ra', 'rb', 'rc'],
        'graphs': ['gb', 'ga']
    },
    "p2": {'ranges': ['oi']},
}

SIMPLIFIED_RANGES = SIMPLIFIED_PREDICATE_DICT["p1"]["ranges"]

SIMPLIFIED_RANGE_GRAPHS = SIMPLIFIED_PREDICATE_DICT["p1"]["graphs"]

PREDICATE_ON_REDIS_RESULT = SIMPLIFIED_PREDICATE_DICT["p1"]

CLASS = {
    u'head': {u'link': [], u'vars': [u'graph', u'videoClass', u'program']},
    u'results': {u'distinct': False,
                 u'bindings': [
                {
                    u'graph': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                    u'program': {u'type': u'uri', u'value': u'http://test.domain.com/base/Programa_Bem_Estar'},
                    u'videoClass': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Video'}
                }],
    u'ordered': True}}

RESULT_DICT_WITH_LANG = {
    u'head': {u'link': [], u'vars': [u'label', u'comment']},
    u'results': {
        u'distinct': False, u'bindings': [
            {u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Pessoa'}},
            {u'comment': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Ser humano, vivo, morto ou fict\xedcio.'}}], u'ordered': True}}

EMPTY_CLASS = {
    u'head': {u'link': [], u'vars': [u'graph', u'videoClass', u'program']},
    u'results': {u'distinct': False, u'bindings': [], u'ordered': True}}


PREDICATE = {
    "head": {"link": [], "vars": ["predicate", "predicate_graph", "type", "range", "label", "tem_valor_unico", "grafo_do_range", "label_do_range"]},
    "results": {"distinct": False, "ordered": True, "bindings": [
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/status_de_publicacao"},
         "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#DatatypeProperty"},
         "predicate_graph": {"type": "uri", "value": "http://test.domain.com/G1/"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"},
         "label": {"type": "literal", "value": "Status de publica\u00E7\u00E3o"}},
        {"predicate": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label"},
         "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#DatatypeProperty"},
         "predicate_graph": {"type": "uri", "value": "http://test.domain.com/G1/"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"},
         "label": {"type": "literal", "value": "Nome popular"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/cita_a_entidade"},
         "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
         "predicate_graph": {"type": "uri", "value": "http://test.domain.com/G1/"},
         "range": {"type": "uri", "value": "http://test.domain.com/G1/MontadoraDeVeiculos"},
         "label": {"type": "literal", "value": "Entidades"},
         "grafo_do_range": {"type": "uri", "value": "http://test.domain.com/G1/"},
         "label_do_range": {"type": "literal", "value": "Montadora de ve\u00EDculos"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/cita_a_entidade"},
         "type": {"type": "uri", "value": "http://www.w3.org/2002/07/owl#ObjectProperty"},
         "predicate_graph": {"type": "uri", "value": "http://test.domain.com/G1/"},
         "range": {"type": "uri", "value": "http://test.domain.com/base/Organizacao"},
         "label": {"type": "literal", "value": "Entidades"},
         "grafo_do_range": {"type": "uri", "value": "http://test.domain.com/"},
         "label_do_range": {"type": "literal", "value": "Organiza\u00E7\u00E3o"}}
    ]}
}


CARDINALITY = {
    "head": {"link": [], "vars": ["predicate", "min", "max", "range"]},
    "results": {"distinct": False, "ordered": True, "bindings": [
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/data_de_criacao_do_conteudo"},
         "max": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/2001/XMLSchema#dateTime"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/data_de_criacao_do_conteudo"}	,
         "min": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/2001/XMLSchema#dateTime"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/status_de_publicacao"},
         "max": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/status_de_publicacao"},
         "min": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"}},
        {"predicate": {"type": "uri", "value": "http://test.domain.com/base/pertence_ao_produto"},
         "min": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://test.domain.com/base/Produto"}},
        {"predicate": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label"},
         "max": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"}},
        {"predicate": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label"},
         "min": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": "1"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"}}]
    }
}

CARDINALITY_WITH_ENUMERATED_VALUE = {
    "head": {"link": [], "vars": ["predicate", "min", "max", "range"]},
    "results": {"distinct": False, "ordered": True, "bindings": [
        {"predicate": {"type": "uri", "value": "http://test.domain.com/predicate_with_enumerated_value"},
         "range": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral"},
         "enumerated_value": {"value": "Masculino"},
         "enumerated_value_label": {"value": "Sexo"}
         }
    ]}
}

FINAL = {
    "class": u"http://test.domain.com/G1/Video",
    "graph": u"http://test.domain.com/",
    "predicates": {
        "http://www.w3.org/2000/01/rdf-schema#label": {
            "type": "http://www.w3.org/2002/07/owl#DatatypeProperty",
            "label": "Nome popular",
            "graph": "http://test.domain.com/G1/",
            "range": {
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral": {
                    "min": "1",
                    "max": "1",
                    "label": "",
                    "graph": ""
                }
            }
        },
        "http://test.domain.com/base/status_de_publicacao": {
            "type": "http://www.w3.org/2002/07/owl#DatatypeProperty",
            "graph": "http://test.domain.com/G1/",
            "label": "Status de publica\u00E7\u00E3o",
            "range": {
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral": {
                    "min": "1",
                    "max": "1",
                    "label": "",
                    "graph": ""
                }
            }
        },
        "http://test.domain.com/base/cita_a_entidade": {
            "type": "http://www.w3.org/2002/07/owl#ObjectProperty",
            "graph": "http://test.domain.com/G1/",
            "label": "Entidades",
            "range": {
                "http://test.domain.com/G1/MontadoraDeVeiculos": {
                    "graph": "http://test.domain.com/G1/",
                    "label": "Montadora de ve\u00EDculos"
                },
                "http://test.domain.com/base/Organizacao": {
                    "graph": "http://test.domain.com/",
                    "label": "Organiza\\u00E7\\u00E3o"
                }
            }
        }
    }
}

FINAL_CLASS_PERSON = {
    "class": u"http://test.domain.com/person/Person",
    "comment": u"Ser humano, vivo, morto ou fictício.",
    "label": u"Pessoa",
    "predicates": FINAL["predicates"]
}


FINAL_REAL = {
    u'head': {
        u'link': [],
        u'vars': [u'predicate', u'predicate_graph', u'type', u'range', u'label', u'tem_valor_unico', u'grafo_do_range', u'label_do_range']
    },
    u'results': {
        u'distinct': False,
        u'bindings': [{
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/trata_do_assunto'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Assunto'},
                u'label_do_range': {u'type': u'literal', u'value': u'Assunto'},
                u'label': {u'type': u'literal', u'value': u'Assuntos'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/trata_do_assunto'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/AssuntoCarro'},
                u'label_do_range': {u'type': u'literal', u'value': u'Assunto de Carros'},
                u'label': {u'type': u'literal', u'value': u'Assuntos'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/trata_do_assunto'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/AssuntoAeroporto'},
                u'label_do_range': {u'type': u'literal', u'value': u'Assuntos de Aeroportos'},
                u'label': {u'type': u'literal', u'value': u'Assuntos'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/type_midia'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                u'label_do_range': {u'type': u'literal', u'value': u'XMLLiteral'},
                u'label': {u'type': u'literal', u'value': u'type de m\xeddia'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/type_midia'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                u'label_do_range': {u'type': u'literal', u'value': u'XMLLiteral'},
                u'label': {u'type': u'literal', u'value': u'type de Midia'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Lugar'},
                u'label_do_range': {u'type': u'literal', u'value': u'Lugar'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/UF'},
                u'label_do_range': {u'type': u'literal', u'value': u'UF'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Endereco'},
                u'label_do_range': {u'type': u'literal', u'value': u'Endere\xe7o'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Criatura'},
                u'label_do_range': {u'type': u'literal', u'value': u'Criatura'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Organizacao'},
                u'label_do_range': {u'type': u'literal', u'value': u'Organiza\xe7\xe3o'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/GrupoMusical'},
                u'label_do_range': {u'type': u'literal', u'value': u'Grupo Musical'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/cita_a_entidade'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/MontadoraDeVeiculos'},
                u'label_do_range': {u'type': u'literal', u'value': u'Montadora de ve\xedculos'},
                u'label': {u'type': u'literal', u'value': u'Entidades'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/faz_parte_da_historia'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Historia'},
                u'label_do_range': {u'type': u'literal', u'value': u'Hist\xf3ria'},
                u'label': {u'type': u'literal', u'value': u'Hist\xf3rias'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/midia_id'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/2001/XMLSchema#integer'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'label': {u'type': u'literal', u'value': u'MidiaID'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/esta_no_canal'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Canal'},
                u'label_do_range': {u'type': u'literal', u'value': u'Canal de TV'},
                u'label': {u'type': u'literal', u'value': u'Est\xe1 no Canal'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/esta_no_programa'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/base/Programa'},
                u'label_do_range': {u'type': u'literal', u'value': u'Programa de TV'},
                u'label': {u'type': u'literal', u'value': u'Est\xe1 no Programa'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/canal_webmedia'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                u'label_do_range': {u'type': u'literal', u'value': u'XMLLiteral'},
                u'label': {u'type': u'literal', u'value': u'Canal na WebMedia'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/G1/cita_a_obra'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/'},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Aeroporto'},
                u'label_do_range': {u'type': u'literal', u'value': u'Aeroporto'},
                u'label': {u'type': u'literal', u'value': u'Produtos e Constru\xe7\xf5es'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/G1/cita_a_obra'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#ObjectProperty'},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'range': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Carro'},
                u'label_do_range': {u'type': u'literal', u'value': u'Carro'},
                u'label': {u'type': u'literal', u'value': u'Produtos e Constru\xe7\xf5es'}
        }, {
                u'predicate': {u'type': u'uri', u'value': u'http://test.domain.com/base/permalink'},
                u'type': {u'type': u'uri', u'value': u'http://www.w3.org/2002/07/owl#DatatypeProperty'},
                u'predicate_graph': {"type": "uri", "value": "http://test.domain.com/G1/"},
                u'grafo_do_range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
                u'range': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral'},
                u'label_do_range': {u'type': u'literal', u'value': u'XMLLiteral'},
                u'label': {u'type': u'literal', u'value': u'Permalink'}
        }],
        u'ordered': True
    }
}


SPARQL_RESULT_LABEL_TYPE_QUERY_1 = {
    "head": {
        "link": [],
        "vars": ["label", "type_label"]
    },
    "results": {
        "distinct": False,
        "ordered": True,
        "bindings": [
            {
                "label": {
                    "type": "literal",
                    "value": "Baixa da Colina"
                },
                "type_label": {
                    "type": "literal",
                    "value": "Bairro"
                }
            }
        ]
    }
}

SPARQL_RESULT_LABEL_TYPE_QUERY_2 = {
    "head": {
        "link": [],
        "vars": ["label", "type_label"]
    },
    "results": {
        "distinct": False,
        "ordered": True,
        "bindings": [
            {
                "label": {
                    "type": "literal",
                    "value": u'Prevent\xf3rio'
                },
                "type_label": {
                    "type": "literal",
                    "value": "Bairro"
                }
            }
        ]
    }
}

SPARQL_RESULT_DETAILS_QUERY_1 = {
    "head": {
        "link": [],
        "vars": ["predicate", "label", "value", "name"]
    },
    "results": {
        "distinct": False,
        "ordered": True,
        "bindings": [
            {
                "predicate": {
                    "type": "uri",
                    "value": "http://test.domain.com/base/nome_completo"
                },
                "label": {
                    "type": "literal",
                    "value": "l1"
                },
                "value": {
                    "type": "uri",
                    "value": "v1"
                }
            },
            {
                "predicate": {
                    "type": "uri",
                    "value": "http://test.domain.com/base/uma_object_property"
                },
                "label": {
                    "type": "literal",
                    "value": "l2"
                },
                "value": {
                    "type": "uri",
                    "value": "http://alguma-uri"
                },
                "name": {
                    "type": "literal",
                    "value": "v2"
                }
            }
        ]
    }
}

SPARQL_RESULT_DETAILS_QUERY_2 = {
    "head": {
        "link": [],
        "vars": ["predicate", "label", "value", "name"]
    },
    "results": {
        "distinct": False,
        "ordered": True,
        "bindings": [
            {
                "predicate": {
                    "type": "uri",
                    "value": "http://test.domain.com/base/nome_completo"
                },
                "label": {
                    "type": "literal",
                    "value": "l3"
                },
                "value": {
                    "type": "uri",
                    "value": "v3"
                }
            }
        ]
    }
}

SUGGEST_PREDICATE_RESPONSE = {u"value": {
    u'http://test.domain.com/base/Bairro_Baixa_da_Colina_Rio_Branco_AC': {
        u"label": u'Baixa da Colina',
        u"type": {u'http://test.domain.com/base/Bairro': u"Bairro"},
        u"detail": [{u"value": u"v1", u"label": u"l1"},
                 {u"value": u"v2", u"label": u"l2"}]
    },
    u'http://test.domain.com/base/Bairro_Preventorio_Rio_Branco_AC': {
        u"label": u'Prevent\xf3rio',
        u"type": {u'http://test.domain.com/base/Bairro': u"Bairro"},
        u"detail": [{u"value": u"v3", u"label": u"l3"}]
    }
}}

SEARCH_API_RESULT = {"page": 1, "page_size": 2, "num_pages": 3, "predicate": {"uri_predicate": "info_predicate"}}

