# OpenEMR Installation using Docker
# OpenEMR Installation Table of contents
- [Check if the Instance is Clean Before Installation](#check-if-the-instance-is-clean-before-installation)
- [(if needed)Deletion comments](#if-neededdeletion-comments)
- [Install Docker](#install-docker)
- [Create Docker Compose](#create-docker-compose)
- [If you have access to volumes (100 patients)](#if-you-have-access-to-volumes100-patients)
- [If you have access to volumes (11k patients)](#if-you-have-access-to-volumes11k-patients)
- [The volumes are created and restored](#the-volumes-are-created-and-restored)
- [Clone DevOps Repo](#clone-devops-repo)
- [Docker Installation Recording (9/8/2023)](#docker-installation-recording-982023)
- [Apache Configuration for HTTPS (if not done by David)](#apache-configuration-for-https-if-not-done-by-david)



## Check if the Instance is Clean Before Installation

```bash
sudo su – oemr
docker ps -a
```

## (if needed)Deletion comments
```bash
docker-compose down
```
## Install docker
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
```
If you face any issues while installing the docker then use the sudo reboot command
(Create oemr user)
```bash
sudo adduser oemr​
```
Enter your password​
Click enter and If the information is correct. Click Y(yes).​

## Create Docker user
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```
(Anything that has docker command should be run by oemr user)
LOGOUT and LOGIN
```bash
sudo su - oemr
docker run hello-world
sudo systemctl enable containerd.service
sudo apt-get install docker-compose -y
sudo su – oemr​
nano docker-compose.yml
```
## Create docker-compose
 Use admin/pass as user/password credentials to login to openemr (from OE_USER and OE_PASS below) 
 MYSQL_HOST and MYSQL_ROOT_PASS are required for openemr 
MYSQL_USER, MYSQL_PASS, OE_USER, MYSQL_PASS are optional for openemr and 
if not provided, then default to openemr, openemr, admin, and pass respectively. 
```yaml
version: '3.1'

services:
  mysql:
    restart: always
    image: mariadb:10.11
    command:['mysqld','--character-set-server=utf8mb4','--innodb_buffer_pool_size=12G'] 
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
      -# 443:443
    volumes:
      - logvolume01:/var/log
      - sitevolume:/var/www/localhost/htdocs/openemr/sites
      - ./custom-php.ini:/etc/php82/php.ini 
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
```
## If you have access to volumes(100 patients)
```bash
sudo apt-get install p7zip-full -y
wget https://go.iu.edu/8qfT
mv 8qfT 3-volumes.zip
unzip 3-volumes.zip
```
## If you have access to volumes(11k patients) 
```bash
sudo apt-get install p7zip-full -y
wget https://go.iu.edu/8qSs 
mv 8qSs 3-volumes.tar.gz 
tar -xvzf 3-volumes.tar.gz
```
## The volumes are created and restored.
```bash
docker volume create oemr_databasevolume
docker volume create oemr_sitevolume
docker volume create oemr_logvolume01
```
```bash
sudo su
cd /var/lib/docker/volumes/
```
use this command to check if the volumes already exist
```bash
ls –al 
```
Remove the volumes if already exist, so that they can replaced by the new volumes
```bash
rm –Rf oemr_databasevolume/​
rm –Rf oemr_logvolume01/​
rm –Rf oemr_sitevolume/
```
use your username in place of oemr
```bash
cp -r /home/oemr/oemr_databasevolume oemr_databasevolume
cp -r /home/oemr/oemr_logvolume01/ oemr_logvolume01
cp -r /home/oemr/oemr_sitevolume/ oemr_sitevolume

chown -Rf oemr:root oemr_databasevolume/_data/
chown -Rf oemr:root oemr_logvolume01/_data/
chown -Rf oemr:root oemr_sitevolume/_data/
```
To check if the volumes have been copied with the right permissions
```bash
ls –al
```
exit
```bash
sudo su - oemr
docker compose up -d
```
Check if the volumes were correctly restored or not.
Start a local connection and check the patient data.

 Check the webpage. If it does not open then check this.
```bash
docker compose up –d​
docker ps –a​
docker exec –it <container id> /bin/sh​
ls –al
```
There should not be any numbers(1008,1001 etc), root in the apache column so to change this we do the change ownership.
```
chown –Rf apache:root .
```
exit

REMEMBER TO CHANGE THE DOCKER COMPOSE to point to these volume locations 
```yml
nano docker-compose.yml
volumes:
  oemr_databasevolume:
    external: true
  oemr_logvolume01:
    external: true
  oemr_sitevolume:
    external: true
```

## Clone devops repo 
```bash
git clone https://github.com/openemr/openemr-devops
chmod +x openemr-devops/docker/openemr/flex-edge/utilities/devtools
chmod +x openemr-devops/docker/openemr/flex-edge/utilities/devtoolsLibrary.source
mkdir ~/bin
curl -L https://raw.githubusercontent.com/openemr/openemr-devops/master/utilities/openemr-cmd/openemr-cmd > ~/bin/openemr-cmd
curl -L https://raw.githubusercontent.com/openemr/openemr-devops/master/utilities/openemr-cmd/openemr-cmd-h > ~/bin/openemr-cmd-h

chmod +x ~/bin/openemr-cmd
chmod +x ~/bin/openemr-cmd-h
```
LOGOUT and LOGIN again

video example
## docker installation recording (9/8/2023) 
https://iu.mediaspace.kaltura.com/media/t/1_qtdvsg1s 

## Apache configuration for HTTPS (if not done by David) 
 enable http proxy
```bash
sudo a2enmod proxy_http
sudo nano /etc/apache2/sites-enabled/default-ssl.conf
```
 This is the configuration (remember to change the SSL certificate to correct server URL name) 
```apache
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
```


