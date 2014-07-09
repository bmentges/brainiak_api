
# This need to be improved, not tested yet
# Compatible with Fedora 20

# export CODE_DIR=~/code
# export BIN_DIR=~/bin


#*********************#
# SYSTEM DEPENDENCIES #
#*********************#

#sudo yum update
#sudo yum -y install $(cat requirements.yum)

#********************#
# OTHER DEPENDENCIES #
#********************#

# Virtuoso
#cd $CODE_DIR; git clone https://github.com/openlink/virtuoso-opensource.git
#cd $CODE_DIR/virtuoso-opensource; git checkout develop/6 #5421d2ea8fd344c1d70d7c99cc77a2051914bdc7
cd $CODE_DIR/virtuoso-opensource; ./autogen.sh
cd $CODE_DIR/virtuoso-opensource; ./configure
cd $CODE_DIR/virtuoso-opensource; make
sudo mkdir -p /var/lib/virtuoso/db/dumps/
sudo chmod 777 /var/lib/virtuoso/db/ -R
echo "export VIRTUOSO_HOME=/var/lib/virtuoso/db/" >> ~/.bashrc
#sudo ln -s $CODE_DIR/virtuoso-opensource/binsrc/tests/isql /usr/bin/isql
#sudo ln -s $CODE_DIR/virtuoso-opensource/binsrc/virtuoso/virtuoso-t /usr/bin/virtuoso-t
cp $CODE_DIR/brainiak_api/setup/fedora/virtuoso.ini $VIRTUOSO_HOME/virtuoso.ini
cd $VIRTUOSO_HOME; virtuoso-t &

# ElasticSearch 0.90.12
#cd $BIN_DIR; wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.12.tar.gz
cd $BIN_DIR; tar -xvzf elasticsearch-0.90.12.tar.gz
$BIN_DIR/elasticsearch-0.90.12/bin/elasticsearch -f &

# ActiveMQ 5.8.0
#cd $BIN_DIR; wget http://archive.apache.org/dist/activemq/apache-activemq/5.8.0/apache-activemq-5.8.0-bin.tar.gz
#cd $BIN_DIR; tar -xvzf apache-activemq-5.8.0-bin.tar.gz
cp $CODE_DIR/brainiak_api/setup/fedora/activemq.xml $BIN_DIR/apache-activemq-5.8.0/conf/activemq.xml # enable stomp
cd $BIN_DIR/apache-activemq-5.8.0; bin/activemq start &

# Redis
redis-server &

#**********************#
# LOAD SAMPLE ONTOLOGY #
#**********************#

cd $CODE_DIR/brainiak_api/resources/ontologies; make create_all
cd $CODE_DIR/brainiak_api/resources/ontologies; make reset_ontologies

#*********************#
# PYTHON DEPENDENCIES #
#*********************#

source /usr/bin/virtualenvwrapper.sh
mkvirtualenv brainiak
cd $CODE_DIR/brainiak_api/; make install

#********************#
# RUN BRAINIAK TESTS #
#********************#

cd $CODE_DIR/brainiak_api/; make unit


