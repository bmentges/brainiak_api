# This need to be improved, not tested yet
# Compatible with Fedora 20

CODE_DIR=~/code
BIN_DIR=~/bin


#*********************#
# SYSTEM DEPENDENCIES #
#*********************#

su -c 'yum update'
yum -y install $(cat requirements.yum)


#********************#
# OTHER DEPENDENCIES #
#********************#

# Virtuoso
cd ~/code; git clone https://github.com/openlink/virtuoso-opensource.git
cd ~/code/virtuoso-opensource; git checkout develop/6 #5421d2ea8fd344c1d70d7c99cc77a2051914bdc7
cd ~/code/virtuoso-opensource; ./autogen.sh
cd ~/code/virtuoso-opensource; ./configure
cd ~/code/virtuoso-opensource; make
sudo mkdir -p /var/lib/virtuoso/db/virtuoso/dumps/
sudo chmod 777 /var/lib/virtuoso/db/ -R
echo "export VIRTUOSO_HOME=/var/lib/virtuoso/db/virtuoso" >> ~/.bashrc
sudo ln -s ~/code/virtuoso-opensource/binsrc/tests/isql /usr/bin/isql
sudo ln -s ~/code/virtuoso-opensource/binsrc/virtuoso/virtuoso-t /usr/bin/virtuoso-t
virtuoso-t -f &

# ElasticSearch 0.90.12
cd ~/bin; wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.12.tar.gz
cd ~/bin; tar -xvzf elasticsearch-0.90.12.tar.gz
cd ~/bin/elasticsearch-0.90.12; bin/elasticsearch -f &

# ActiveMQ 5.8.0
cd ~/bin; wget http://archive.apache.org/dist/activemq/apache-activemq/5.8.0/apache-activemq-5.8.0-bin.tar.gz
cd ~/bin; tar -xvzf apache-activemq-5.8.0-bin.tar.gz
cp activemq.xml ~/bin/apache-activemq-5.8.0-bin/conf/activemq.xml # enable stomp
cd ~/bin/apache-activemq-5.8.0; bin/activemq start &

#********************#
#    SOURCE CODE     #
#********************#

# Brainiak source code
cd ~/code; git clone https://github.com/globoi/brainiak_api.git    

# Sample ontology
cd ~/code; git clone https://github.com/globoi/upper_ontology.git

#********************#
#   LOAD ONTOLOGY    #
#********************#

cd ~/code/upper_ontology; make create_all
cd ~/code/upper_ontology; make reset_ontologies

#*********************#
# PYTHON DEPENDENCIES #
#*********************#

source /usr/bin/virtualenvwrapper.sh
mkvirtualenv brainiak
cd ~/code/brainiak_api/; make install

#********************#
# RUN BRAINIAK TESTS #
#********************#

cd ~/code/brainiak_api/; make run

