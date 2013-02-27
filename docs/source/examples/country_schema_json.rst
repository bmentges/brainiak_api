.. highlight:: json

::

    {
        "schema": {
            "comment": "Sub-divisão política do Mundo.",
            "links": [
                {
                    "href": "/place/collection/Region",
                    "rel": "place:Region"
                },
                {
                    "href": "/xsd/collection/float",
                    "rel": "xsd:float"
                },
                {
                    "href": "/xsd/collection/float",
                    "rel": "xsd:float"
                },
                {
                    "href": "/upper/collection/Substance",
                    "rel": "upper:Substance"
                },
                {
                    "href": "/upper/collection/Entity",
                    "rel": "upper:Entity"
                },
                {
                    "href": "/upper/collection/Entity",
                    "rel": "upper:Entity"
                }
            ],
            "title": "País",
            "@id": "place:Country",
            "@context": {
                "upper": "http://semantica.globo.com/upper/",
                "place": "http://semantica.globo.com/place/",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "@language": "pt"
            },
            "$schema": "http://json-schema.org/draft-03/schema#",
            "type": "object",
            "properties": {
                "upper:foundingDate": {
                    "comment": "Data de fundação de uma organização ou cidade.",
                    "graph": "upper",
                    "format": "date",
                    "type": "string",
                    "title": "Data de fundação"
                },
                "upper:hasPart": {
                    "comment": "Relação inversa a 'isPartOf', onde quem 'domina' a relação é o elemento 'maior' (e.g. <Country_Brazil> dc:isPartOf <UF_RJ>).",
                    "format": "uri",
                    "graph": "upper",
                    "title": "Tem parte",
                    "range": {
                        "graph": "upper",
                        "@id": "upper:Entity",
                        "title": "Entidade"
                    },
                    "type": "string"
                },
                "upper:name": {
                    "minItems": "1",
                    "graph": "upper",
                    "type": "string",
                    "comment": "Nomes populares de uma instância. Exemplo: nomes pelo quais uma pessoa é conhecida (e.g. Ronaldinho, Zico, Lula). Não confundir com nome completo, uma outra propriedade com valor único e formal.",
                    "title": "Nome"
                },
                "upper:sociallyRelatedWith": {
                    "comment": "Relação social abstrata entre qualquer combinação de (Agente, Objeto) tomados dois-a-dois.",
                    "format": "uri",
                    "graph": "upper",
                    "title": "Socialmente relacionado a",
                    "range": {
                        "graph": "upper",
                        "@id": "upper:Substance",
                        "title": "Substância"
                    },
                    "type": "string"
                },
                "place:longitude": {
                    "comment": "Coordenada de longitude de acordo com WGS84.",
                    "format": "uri",
                    "graph": "place",
                    "title": "Longitude",
                    "range": {
                        "graph": "",
                        "@id": "xsd:float",
                        "title": ""
                    },
                    "type": "string"
                },
                "upper:description": {
                    "comment": "Descrição textual da entidade.",
                    "graph": "upper",
                    "type": "string",
                    "title": "Descrição"
                },
                "place:hasSubRegion": {
                    "comment": "Um lugar pode ser subdividido em regiões.",
                    "format": "uri",
                    "graph": "place",
                    "title": "Tem sub-região",
                    "range": {
                        "graph": "place",
                        "@id": "place:Region",
                        "title": "Região"
                    },
                    "type": "string"
                },
                "place:latitude": {
                    "comment": "Coordenada de latitude de acordo com WGS84.",
                    "format": "uri",
                    "graph": "place",
                    "title": "Latitude",
                    "range": {
                        "graph": "",
                        "@id": "xsd:float",
                        "title": ""
                    },
                    "type": "string"
                },
                "upper:isPartOf": {
                    "comment": "Um recurso (sujeito) que está física ou logicamente incluído em outro (objeto ou valor) (e.g. <UF_RJ> upper:isPartOf <Country_Brazil> ou <Pessoa_Romario> upper:isPartOf <Partido_PSB>).",
                    "format": "uri",
                    "graph": "upper",
                    "title": "É parte de",
                    "range": {
                        "graph": "upper",
                        "@id": "upper:Entity",
                        "title": "Entidade"
                    },
                    "type": "string"
                },
                "place:geonameId": {
                    "comment": "ID para uso da API do Geonames.",
                    "graph": "place",
                    "type": "integer",
                    "title": "ID no Geoname"
                },
                "upper:acronym": {
                    "comment": "Sigla. Ex: SP, RJ, NYC",
                    "graph": "upper",
                    "type": "string",
                    "title": "Sigla"
                },
                "upper:fullName": {
                    "comment": "Nome completo de Agente ou Objeto.",
                    "graph": "upper",
                    "type": "string",
                    "title": "Nome"
                }
            }
        }

    }
