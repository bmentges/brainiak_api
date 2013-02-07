brainiak
++++++++

Brainiak is a Linked Data RESTful API that provides a simple interface with SPARQL endpoints.

Dependencies
============

Can be installed using virtualenv: ::

    sudo pip install virtualenv
    sudo pip install virtualenvwrapper
    source `which virtualenvwrapper.sh`

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
    the Free Software Foundation, either version 2 of the License.

    Brainiak is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Brainiak. If not, see <http://www.gnu.org/licenses/>.