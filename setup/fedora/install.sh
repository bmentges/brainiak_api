#! /bin/sh

# This need to be improved, not tested yet
# Compatible with Fedora 20

set -e

# export CODE_DIR=~/code
# export BIN_DIR=~/bin


#*********************#
# SYSTEM DEPENDENCIES #
#*********************#

sudo su -p
yum -y update
yum -y install $(cat requirements.yum)

#********************#
# OTHER DEPENDENCIES #
#********************#

# Virtuoso

su $USER
    cd $CODE_DIR
    git clone https://github.com/openlink/virtuoso-opensource.git
    cd virtuoso-opensource
    git checkout 5421d2ea8fd344c1d70d7c99cc77a2051914bdc7 # develop/6
    ./autogen.sh
    ./configure
    make
exit

ln -s $CODE_DIR/virtuoso-opensource/binsrc/tests/isql /usr/bin/isql
ln -s $CODE_DIR/virtuoso-opensource/binsrc/virtuoso/virtuoso-t /usr/bin/virtuoso-t

mkdir -p /var/lib/virtuoso/db/dumps/
chmod 777 /var/lib/virtuoso/db/ -R

su $USER
    echo "export VIRTUOSO_HOME=/var/lib/virtuoso/db/" >> ~/.bashrc
    cp $CODE_DIR/brainiak_api/setup/fedora/virtuoso.ini $VIRTUOSO_HOME/virtuoso.ini
    cd $VIRTUOSO_HOME
    virtuoso-t &
exit

# ElasticSearch 0.90.12
su $USER
    cd $BIN_DIR
    wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.12.tar.gz
    tar -xvzf elasticsearch-0.90.12.tar.gz
    elasticsearch-0.90.12/bin/elasticsearch -f &

# ActiveMQ 5.8.0
    cd $BIN_DIR
    wget http://archive.apache.org/dist/activemq/apache-activemq/5.8.0/apache-activemq-5.8.0-bin.tar.gz
    tar -xvzf apache-activemq-5.8.0-bin.tar.gz
    cp $CODE_DIR/brainiak_api/setup/fedora/activemq.xml $BIN_DIR/apache-activemq-5.8.0/conf/activemq.xml # enable stomp
    cd apache-activemq-5.8.0
    bin/activemq start &

# Redis
    redis-server &

#**********************#
# LOAD SAMPLE ONTOLOGY #
#**********************#

    cd $CODE_DIR/brainiak_api/resources/ontologies
    make create_all
    make reset_ontologies

#*********************#
# PYTHON DEPENDENCIES #
#*********************#

    source /usr/bin/virtualenvwrapper.sh
    mkvirtualenv brainiak
    cd $CODE_DIR/brainiak_api/
    make install

#********************#
# RUN BRAINIAK TESTS #
#********************#

    cd $CODE_DIR/brainiak_api/
    make unit

exit
