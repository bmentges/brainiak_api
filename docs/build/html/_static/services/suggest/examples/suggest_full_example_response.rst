.. highlight:: json

::

    {
      "items": [
         {
          "@id": "http://semantica.globo.com/esportes/Atleta/Ronaldo", 
          "title": "Ronaldinho o Fenômeno" 
          "@type": "http://semantica.globo.com/esportes/Atleta",  
          "type_title": "Atleta",
          "class_fields": {
              "base:thumbnail": "http://s-ct.glbimg.globoi.com/jo/eg/static/semantica/img/icones/ico_criatura.png",
          },
          "instance_fields" : [
              {"predicate_id": "rdfs:label", 
               "predicate_title": "Nome" 
               "object_id":"http://semantica.globo.com/esportes/Atleta/Ronaldo", 
               "object_title": "Ronaldo O Fenômeno",
               "required": true,
              },      
              {"predicate_id": "esportes:esta_no_time", 
               "predicate_title": "Pertence ao Time" 
               "object_id":"http://semantica.globo.com/esportes/Equipe/Botafogo", 
               "object_title": "Botafogo" 
               "required": false,
              },
              {"predicate_id": "esportes:posicao", 
               "predicate_title": "Posição" 
               "object_title": "VOL" 
               "required": false,
              }      

         ],
      },
      "item_count": 1,
      "@context": {"esportes": "http://semantica.globo.com/esportes/"}
    }