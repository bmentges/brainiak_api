Troubleshooting
===============

When Brainiak is not working as expected this is the first place to look!


I receive error 404 with message 'X-Brainiak-Client-Id' is not known
--------------------------------------------------------------------

The Brainiak uses the triplestore.ini to multiplex access to different backend triplestore databases.
The value passed in the header ``X-Brainiak-Client-Id`` is the key used to indentify which triplestore is the target endpoint.
If no header ``X-Brainiak-Client-Id`` is given, the default entry is used as target.
The message  "{"errors": ["HTTP error: 404\nClient-Id provided at 'X-Brainiak-Client-Id' (My client_id) is not known"]}" is
returned with error 404, when the key (in the example 'My client_id') is not present in the configuration file triplestore.ini.


How to check if Brainiak is connected with the backend triplestore?
---------------------------------------------------------------------

Any access to /status/virtuoso will yield the connectivity status with the triple store.

 - Virtuoso connection not-authenticated | FAILED | http://localhost:8890/sparql-auth | Unauthorized
 - Virtuoso connection authenticated [api-semantica:[Nu��o�˨e'��Ǟ] | SUCCEED | http://localhost:8890/sparql-auth

There are two independent attempts to connect to Virtuoso.
The first line above represents the status of unauthenticated access, and the second line the status of authenticated access.
You both lines have status FAILED then Brainiak is disconnected with the triplestore.
In the example above, the second line shows that Brainiak can access the database with the configured user "api-semantica".


How to check if Brainiak is connected with the ActiveMQ?
---------------------------------------------------------

Any access to /status/activemq will yield the connectivity status with ActiveMQ.

    ActiveMQ connection not-authenticated | SUCCEED | localhost:61613

The line above shows a successful connection with ActiveMQ.
In case of failure, the user should receive a message like:

    ActiveMQ connection not-authenticated | FAILED | localhost:61613 | 'stomp.exception.NotConnectedException'



Any service gives me the message: "Access to backend service failed"?
----------------------------------------------------------------------

If you are getting the error message below, it means that the triplestore is not accessible by Brainiak.

error response::

    {
        error:
            HTTP error: 500
            Access to backend service failed.  HTTP 599: Failed connect to localhost:8890; Connection refused. Check Virtuoso
    }

In this case, check:
 * are the user and password defined by Brainiak in the environment (or in settings.py) correct ?
 * is Virtuoso up and running ?
 * does the machine (in which Brainiak is installed) has access to the Virtuoso database ?


When filtering instances using ``p`` and ``o`` I only get "HTTP error: 404". But when I only use ``p``, it lists items containing the ``o`` I defined. What am I doing wrong?
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Brainiak is internationalized. It is possible that the value mapped by ``o`` is in some specific language, eg. "London"@en or "Londres"@pt.
Try adding to the query string:

 * ``lang=en``, for English
 * ``lang=pt``, for Portuguese
 * or ``lang=undefined``, if the word is not internationalized


E.g, the request below returns 404:

.. code-block:: http

  GET 'http://brainiak.semantica.dev.globoi.com/G1/Materia/?p1=base:status_de_publicacao&o1=P&p2=G1:cita_a_entidade&o2=http://semantica.globo.com/base/UF_MA'

While this second request is successful:

.. code-block:: http

  GET 'http://brainiak.semantica.dev.globoi.com/G1/Materia/?p1=base:status_de_publicacao&o1=P&p2=G1:cita_a_entidade&o2=http://semantica.globo.com/base/UF_MA&lang=undefined'
