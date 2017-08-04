#!/bin/bash

#
# Questo e' il file di provisioning per la VM iniziata da Vagrant.
# Questo file viene eseguito da Vagrant per fare il provisioning dell'ambiente.
#

JORVIK_DIRECTORY=/vagrant
cd $JORVIK_DIRECTORY

sudo bash config/provision-psql.sh
sudo apt-get upgrade
sudo apt-get install -y --force-yes git python3-pip binutils libproj-dev gdal-bin python3-dev libmysqlclient-dev libjpeg-dev libpq-dev libxml2-dev libxslt-dev

sudo mkdir -p /log/
sudo chmod a+rw /log/


echo "Installazione dei requisiti Python..."
sudo pip3 install -q -r requirements.txt

echo "Configurazione installazione..."
cat <<EOL > config/pgsql.cnf
[client]
host = localhost
port = 5432
database = jorvik
user = jorvik
password = jorvik
EOL

#python3 manage.py migrate
python3 manage.py collectstatic --noinput
