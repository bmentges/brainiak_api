Run Brainiak API at Fedora 20
=============================

Internaly at Globo.com, Capistrano and Pupppet recipes are used for deploying Brainiak.
This scripts are not open source.

The following steps describe step-to-step how to run Brainiak in a fresh Fedora installation, from scratch.

It has been tested on:
- Fedora 20
- Brainiak 2.6.0 release

We'll try to keep it up-to-date. You're invited to help us in this regard ;)

First, if you haven't done yet, it is useful to create directories for:
- source code
- binary

You can re-use some default system folder (e.g. /usr/bin/).
To make the setup less intrusive and understand Brainiak dependencies, you might create the following directories: ::

    mkdir ~/code
    mkdir ~/bin

Feel free to use other directories!
Just make sure you set the right paths when defining CODE_DIR and BIN_DIR environment variables: ::

    echo "export CODE_DIR=~/code" >> ~/.bashrc 
    echo "export BIN_DIR=~/bin" >> ~/.bashrc
    source ~/.bashrc

The setup scripts will used this two environment variables.

Make sure you have git installed... ::

    sudo yum -y install git

... so you can download Brainiak source code (clone project repository): ::

    cd ~/code
    git clone https://github.com/globoi/brainiak_api.git

Once this is done, get into Brainiak Fedora setup directory: ::

    cd brainiak_api/setup/fedora

Allow execution of the setup scripts: ::

    chmod +x *.sh

And run: ::

    ./install.sh

This will take quite some time. The times below ocurred in a Virtual Machine with 1GB RAM and 8GB disk.

What exactly this script does?

- Update default yum packages (~20 min to update 1084 packages)
- Install dependencies which are available at default Fedora repository (~4 min)
- Download Virtuoso from source code and build it (~10min). This is needed because the Virtuoso package currently available at Fedora repository (version 6.1.6, release 5.fc20) has bugs (e.g. modify doesn't delete triples before adding new ones)
- Run Virtuoso
- Download ElasticSearch binary and run it
- Download ActiveMQ binary and run it
- Load sample ontology
- Install packaging management tools for Python (pip, virtualenv, virtualenvwrapper)
- Create a Python virtual environment called brainiak, with all python packages which are dependencies for Brainiak
- Run Brainiak tests to check if everything is fine
