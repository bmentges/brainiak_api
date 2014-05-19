Building Brainiak in your local environment
===========================================

Brainiak is developed using Python_ 2.7 and the web framework Tornado_, on top of Virtuoso_.

.. _Tornado: http://www.tornadoweb.org/en/stable/
.. _Python: http://python.org
.. _Virtuoso: http://virtuoso.openlinksw.com/

Source-code
-----------

Clone Brainiak repository using Git_:

.. _Git: http://git-scm.com/

.. code-block:: bash

  git clone git://ngit.globoi.com/brainiak/brainiak.git

Or, if you have super-powers:

.. code-block:: bash

  git clone git@ngit.globoi.com:brainiak/brainiak.git


Python dependencies
-------------------

Python 2.7
++++++++++

Most recent GNU Linux and MacOS distributions have Python_ installed by default. If this is not your case, `download and install it <http://www.python.org/download/releases/2.7/>`_.

Python libs
+++++++++++

We strongly suggest you use VirtualEnv_ and VirtualEnvWrapper_, to isolate dependencies of each Python project you run locally:

.. _VirtualEnv: http://www.virtualenv.org/
.. _VirtualEnvWrapper: http://virtualenvwrapper.readthedocs.org/en/latest/

.. code-block:: bash

  $ sudo python easy_install setuptools
  $ sudo python easy_install pip
  $ sudo pip install virtualenv virtualenvwrapper
  $ source `which virtualenvwrapper.sh`
  $ mkvirtualenv brainiak

To install other python packages, make sure you enter Brainiak root directory and run:

.. code-block:: bash

  $ make install


Non-python dependencies
-----------------------

When running Brainiak locally, you can refer a local or remote Virtuoso_ server.

Brainiak access to Virtuoso_ is defined in the `settings.py` file, at `brainiak/src/brainiak` directory, by the lines:

.. code-block:: python

  SPARQL_ENDPOINT = 'http://localhost:8890/sparql-auth'
  SPARQL_ENDPOINT_USER = "api-semantica"
  SPARQL_ENDPOINT_PASSWORD = "api-semantica"
  SPARQL_ENDPOINT_AUTH_MODE = "digest"
  SPARQL_ENDPOINT_REALM = "SPARQL"

In order to point your local Brainiak to DEV's Virtuoso, for instance, `SPARQL_ENDPOINT` could be changed to:

.. code-block:: python

  SPARQL_ENDPOINT = "http://dev.virtuoso.globoi.com:8890/sparql-auth"

Note that **digest authentication is mandatory** for Brainiak's access to Virtuoso. Therefore, make sure `SPARQL_ENDPOINT_USER` and `SPARQL_ENDPOINT_PASSWORD` are appropriately set. 

The steps below should be followed just if you are installing Virtuoso locally.

OpenLink Virtuoso
+++++++++++++++++

Virtuoso_ is a middleware and hybrid database engine that combines the functionalities of RDBMS, ORDBMS, virtual database, RDF, XML, free-text, web application server and file server. 

Internally, Brainiak uses Virtuoso_ as an Object-relational database (throught RDF_).


.. _RDF: http://en.wikipedia.org/wiki/Resource_Description_Framework

*Version*: Virtuoso Open Source Edition (multi threaded) 6.1

Install in MacOS X
******************

Using HomeBrew_:

.. _HomeBrew: http://mxcl.github.com/homebrew/

.. code-block:: bash

  $ sudo brew install virtuoso


Install in Fedora
*****************

.. code-block:: bash

  $ sudo yum install virtuoso


After-installing Virtuoso
+++++++++++++++++++++++++

Run isql (OpenLink Interactive SQL) prompt:

.. code-block:: bash

  $ isql
  OpenLink Interactive SQL (Virtuoso), version 0.9849b.
  Type HELP; for help and EXIT; to exit.
  SQL> 

And execute the steps bellow from it.

Add authenticated user
**********************

Create an user `api-semantica` with password `api-semantica`, and grant it update permissions, using the following commands:

.. code-block:: bash

  SQL> DB.DBA.USER_CREATE ('api-semantica', 'api-semantica');
  SQL> grant SPARQL_UPDATE to "api-semantica";

Activate inference in graphs
****************************

Some Brainiak primitives make queries to Virtuoso using inference. To make sure this primitives will work appropriatelly, you have to enable associate Brainiak ruleset for all your graphs, **after loading instances to your graphs**.

Brainiak, by default, uses inference in all graphs that are mapped to the rule named 'http://semantica.globo.com/ruleset'.

For instance, to apply Brainiak ruleset 'http://semantica.globo.com/ruleset' to the graph `http://semantica.globo.com/new_graph`, run:

.. code-block:: bash

  SQL> rdfs_rule_set('http://semantica.globo.com/ruleset', 'http://semantica.globo.com/new_graph'); 

For more information about this function, read fn_rdfs_rule_set_ documentation at OpenLink's website.

.. _fn_rdfs_rule_set: http://docs.openlinksw.com/virtuoso/fn_rdfs_rule_set.html