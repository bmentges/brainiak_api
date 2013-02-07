brainiak
++++++++

Brainiak is a Linked Data RESTful API that provides access to SPARQL endpoints.

Motivation
==========

The following topics motivated the development of Brainiak:

* Lower the barrier to use semantic technlogies
* Encapsulate the access to triple stores compatible with RDF/TURTLE and SPARQL (e.g. `OpenLink Virtuoso <http://virtuoso.openlinksw.com/>`_, `Sesame <http://www.aduna-software.com/technology/sesame>`_, `AllegroGraph <http://www.franz.com/agraph/allegrograph/>`_, `Ontotext OWLIM <http://www.ontotext.com/owlim>`_)
* Provide data governance to triple stores
* Provide a unique and coherent interface to other database backends, including non triple stores (e.g.: `ElasticSearch <http://www.elasticsearch.org/>`_).

Dependencies
============


Brainiak is developed using `Python <http://www.python.org/>`_.

Can be installed using `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_: ::

    # Install virtualenv / virtualenvwraper, in case you didn't yet:
    sudo pip install virtualenv
    sudo pip install virtualenvwrapper
    source `which virtualenvwrapper.sh`

    # Then, just use it:
    mkvirtualenv brainiak
    workon brainiak
    make install

Or using super-user powers: ::

    sudo make install

Run
===

At development environments: ::

    make run

Test
====

Check if everything is running as expected, and keep up the code covered with tests when contributing: ::

    make test

License
=======

Brainiak is GNU GPL 2: ::

    < Brainiak: Linked Data RESTful API >
    Copyright (C) 2013 - Globo.com

    Brainiak is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation,  version 2 of the License.

    Brainiak is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Brainiak. If not, see <http://www.gnu.org/licenses/>.