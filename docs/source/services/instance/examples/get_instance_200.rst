.. highlight:: json

::

    {

        "rdfs:label": "Brazil",
        "rdf:type": "place:Country",
        "links": [
            {
                "href": "http://localhost:5100/place/Country/Brazil",
                "rel": "self"
            },
            {
                "href": "http://localhost:5100/place/Country/_schema",
                "rel": "describedBy"
            },
            {
                "href": "http://localhost:5100/place/Country/Brazil",
                "method": "PATCH",
                "rel": "edit"
            },
            {
                "href": "http://localhost:5100/place/Country/Brazil",
                "method": "DELETE",
                "rel": "delete"
            }
        ],
        "rdfs:comment": "Representa o país Brasil.",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "place": "http://semantica.globo.com/place/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "$schema": "http://localhost:5100/place/Country/_schema",
        "@id": "http://localhost:5100/place/Country/Brazil",
        "@type": "place:Country"

    }
