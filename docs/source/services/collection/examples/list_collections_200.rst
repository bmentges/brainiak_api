.. highlight:: json

::

    {
        "items": [
            {
                "@id": "place:Place",
                "title": "Lugar"
            },
            {
                "@id": "place:Continent",
                "title": "Continente"
            },
            {
                "@id": "place:PostalAddress",
                "title": "Endereço"
            },
            {
                "@id": "place:Country",
                "title": "País"
            },
            {
                "@id": "place:GeopoliticalDivision",
                "title": "Região Administrativa"
            },
            {
                "@id": "place:Neighborhood",
                "title": "Bairro"
            },
            {
                "@id": "place:City",
                "title": "Cidade"
            },
            {
                "@id": "place:Region",
                "title": "Região"
            },
            {
                "@id": "place:State",
                "title": "Estado"
            }
        ],
        "item_count": 9,
        "links": [
            {
                "href": "http://api.semantica.dev.globoi.com/place/",
                "rel": "self"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/",
                "rel": "list"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/{resource_id}",
                "rel": "item"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/",
                "method": "POST",
                "rel": "create"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/{resource_id}",
                "method": "DELETE",
                "rel": "delete"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/{resource_id}",
                "method": "PUT",
                "rel": "replace"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/?page=1",
                "method": "GET",
                "rel": "first"
            },
            {
                "href": "http://api.semantica.dev.globoi.com/place/?page=1",
                "method": "GET",
                "rel": "last"
            }
        ],
        "@context": {
            "place": "http://semantica.globo.com/place/",
            "@language": "pt"
        }

    }
