#!/bin/bash
 

# Add a new user and group 'csye6225' 
sudo groupadd csye6225
sudo useradd -r -g csye6225 -s /usr/sbin/nologin csye6225

sudo yum install -y git

cd ~/webapp

sudo yum install -y python38 python38-pip

python3.8 -m pip install --user --upgrade pip
python3.8 -m venv venv
source venv/bin/activate

sudo yum install -y mariadb-server
# Start and enable MariaDB service
sudo systemctl start mariadb
sudo systemctl enable mariadb
 
sudo mysql_secure_installation <<EOF
 
y
root
root
y
y
y
y
EOF

sudo mysql -uroot -proot -e "CREATE DATABASE Users;"
 
sudo yum install -y pkg-config
sudo yum install -y mysql-devel

pip3.8 install -r requirements.txt

pip3.8 install pytest flask-testing python-dotenv cryptography flask-sqlalchemy flask-migrate flask-bcrypt flask-httpauth pymysql

sudo echo "SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:root@localhost/Users" > .env

mysql -uroot -proot -e "SHOW DATABASES;"
 
export FLASK_APP=app2.py
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
 
# Add your systemd service file to /etc/systemd/system
sudo cp ~/flaskapp.service /etc/systemd/system/flaskapp.service

# Reload the systemd daemon to recognize the new service
sudo systemctl daemon-reload
 
# Enable the service to start on boot
sudo systemctl enable flaskapp.service

# Clean up cache and update the system
sudo yum clean all