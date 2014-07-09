Brainiak
++++++++

Brainiak is a Linked Data RESTful API to provide transparent access to SPARQL endpoints.

This a project created by Globo.com's engineers to enhace its semantic platform.
We are releasing this as an open-source project in order to give something back to the software community.

DISCLAIMER
==========

The project is released as it is.
This means you might have to tweak it, in order to meet your purpose.
People can contribute to turn this project more adoption-friendly outside its original context of creation and use.

For this purpose, use the forum https://groups.google.com/forum/#!forum/brainiak_api_users to discuss ideas and ask questions.

We use the twitter https://twitter.com/brainiak_api to also broadcast information about the project and related subjects.


Motivation
==========

The following topics motivated the development of Brainiak:

* Lower the barrier to use semantic technlogies
* Encapsulate the access to triple stores compatible with RDF/TURTLE and SPARQL (e.g. `OpenLink Virtuoso <http://virtuoso.openlinksw.com/>`_, `Sesame <http://www.aduna-software.com/technology/sesame>`_, `AllegroGraph <http://www.franz.com/agraph/allegrograph/>`_, `Ontotext OWLIM <http://www.ontotext.com/owlim>`_)
* Enhance data management to triple stores
* Provide a unique and coherent interface to other database backends, including non triple stores (e.g.: `ElasticSearch <http://www.elasticsearch.org/>`_).

Documentation
=============

Internally at Globo.com, the docs are available at http://brainiak.semantica.globoi.com/docs/
After public release we will publish the docs probably at https://brainiak.readthedocs.org

Running
=======

Brainiak is developed using `Python <http://www.python.org/>`_.

It can be installed using `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_: ::

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

After virtualenv is ready (run in development mode): ::

    make run

Brainiak will be available at: http://localhost:5100/

Testing
=======

Check if everything is running as expected, and keep up the code covered with tests when contributing: ::

    make test

License
=======

Brainiak is GNU GPL 2: ::

    < Brainiak: Linked Data RESTful API >
    Copyright (C) 2013 - Globo.com

    Brainiak is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    Brainiak is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Brainiak. If not, see <http://www.gnu.org/licenses/>.

