# OpenEMR Installation using Docker

# Check if Instances are Clean Before Installation

```bash
sudo su – oemr
docker ps -a
# (if needed)Deletion comments
docker-compose down
docker exec -it "container ID" /bin/bash
rm -Rf "volumes"
ls –al  # to check if properly deleted
#install docker
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
sudo groupadd docker
sudo usermod -aG docker $USER
#LOGOUT and LOGIN
docker run hello-world
sudo systemctl enable containerd.service
sudo apt-get install docker-compose -y
#Create docker-compose
# Use admin/pass as user/password credentials to login to openemr (from OE_USER and OE_PASS below) 
# MYSQL_HOST and MYSQL_ROOT_PASS are required for openemr 
# MYSQL_USER, MYSQL_PASS, OE_USER, MYSQL_PASS are optional for openemr and 
#      if not provided, then default to openemr, openemr, admin, and pass respectively. 
version: '3.1'

services:
  mysql:
    restart: always
    image: mariadb:10.6
    command: ['mysqld', '--character-set-server=utf8mb4']
    volumes:
      - databasevolume:/var/lib/mysql
    ports:
      - 3306:3306
    environment:
      MYSQL_ROOT_PASSWORD: root

  openemr:
    restart: always
    image: openemr/openemr:7.0.2
    ports:
      - 8080:80
      # - 443:443
    volumes:
      - logvolume01:/var/log
      - sitevolume:/var/www/localhost/htdocs/openemr/sites
      # - /home/oemr/openemr-devops/docker/openemr/flex-edge/utilities/:/root/
    environment:
      MYSQL_HOST: mysql
      MYSQL_ROOT_PASS: root
      MYSQL_USER: openemr
      MYSQL_PASS: openemr
      OE_USER: admin
      OE_PASS: pass
    depends_on:
      - mysql

volumes:
  logvolume01: {}
  sitevolume: {}
  databasevolume: {}
#If you have access to volumes 
sudo apt-get install p7zip-full -y
wget https://go.iu.edu/8qfT
mv 8qfT 3-volumes.zip
unzip 3-volumes.zip
#docker volumes correct restored 
docker volume create oemr_databasevolume
docker volume create oemr_sitevolume
docker volume create oemr_logvolume01

sudo su
cd /var/lib/docker/volumes/
cp -r /home/oemr/oemr_databasevolume oemr_databasevolume
cp -r /home/oemr/oemr_logvolume01/ oemr_logvolume01
cp -r /home/oemr/oemr_sitevolume oemr_sitevolume

chown -Rf oemr:root oemr_databasevolume/_data/
chown -Rf oemr:root oemr_logvolume01/_data/
chown -Rf oemr:root oemr_sitevolume/_data/
#exit
exit
sudo su - oemr
docker-compose up -d
#REMEMBER TO CHANGE THE DOCKER COMPOSE to point to these volume locations 
nano docker-compose.yml
volumes:
  oemr_databasevolume:
    external: true
  oemr_logvolume01:
    external: true
  oemr_sitevolume:
    external: true
#Clone devops repo 
git clone https://github.com/openemr/openemr-devops
chmod +x openemr-devops/docker/openemr/flex-edge/utilities/devtools
chmod +x openemr-devops/docker/openemr/flex-edge/utilities/devtoolsLibrary.source
mkdir ~/bin
curl -L https://raw.githubusercontent.com/openemr/openemr-devops/master/utilities/openemr-cmd/openemr-cmd > ~/bin/openemr-cmd
curl -L https://raw.githubusercontent.com/openemr/openemr-devops/master/utilities/openemr-cmd/openemr-cmd-h > ~/bin/openemr-cmd-h

chmod +x ~/bin/openemr-cmd
chmod +x ~/bin/openemr-cmd-h

#LOGOUT and LOGIN again
#video example
#docker installation recording (9/8/2023) 
https://iu.mediaspace.kaltura.com/media/t/1_qtdvsg1s 
# Apache configuration for HTTPS (if not done by David) 
# enable http proxy 
sudo a2enmod proxy_http
sudo nano /etc/apache2/sites-enabled/default-ssl.conf
# This is the configuration (remember to change the SSL certificate to correct server URL name) 
<IfModule mod_ssl.c>
  <VirtualHost _default_:443>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    SSLEngine on
    SSLCertificateFile /etc/apache2/in-info-web19.luddy.iupui.edu.crt
    SSLCertificateKeyFile /etc/apache2/in-info-web19.luddy.iupui.edu.key
    SSLCertificateChainFile /etc/apache2/in-info-web19.luddy.iupui.edu.interm.crt
    <FilesMatch "\.(cgi|shtml|phtml|php)$">
      SSLOptions +StdEnvVars
    </FilesMatch>
    <Directory /usr/lib/cgi-bin>
      SSLOptions +StdEnvVars
    </Directory>
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
  </VirtualHost>
</IfModule>
## Run SQL to import CPT4 
# File in EHR-dev channel - cpt4_final.sql 




