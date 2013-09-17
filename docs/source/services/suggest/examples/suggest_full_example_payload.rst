.. highlight:: json

::

    {
        "search": {
            "pattern": "Ronaldo",
            "target": "http://semantica.globo.com/base/cita_a_entidade",
            "fields": ["http://semantica.globo.com/upper/name", 
                          "http://semantica.globo.com/upper/fullName", 
                          "base:dados_buscaveis"],
            "graphs": ["http://semantica.globo.com/esportes/"],
            "classes": [
                "http://semantica.globo.com/esportes/Atleta",
                "http://semantica.globo.com/esportes/Equipe" 
            ]

        },
        "response": {
            "required_fields": false,
            "meta_fields": ["metadata:disambiguationProperty", "base:detalhe_da_cortina"],
            "class_fields": ["base:thumbnail"],
            "classes": [
                {
                    "@type": "http://semantica.globo.com/esportes/Atleta",
                    "instance_fields": ["esportes:esta_no_time", "esportes:posicao"],
               },
                {
                    "@type": "http://semantica.globo.com/esportes/Equipe",
                    "instance_fields": ["base:esta_na_cidade"]
              }
            ]

        }
    }