sudo apt-get install nginx

cp ./tools350_nginx.conf /etc/nginx/sites-available/tools350_nginx.conf
ln -s /etc/nginx/sites-available/tools350_nginx.conf /etc/nginx/sites-enabled/tools350_nginx.conf

cd ~/350-tools-mk2
# Assumes pipenv installed, tested with python3.8.1
pipenv install 
nohup uwsgi --socket tools350.sock --module tools350.wsgi --chmod-socket=666 &

sudo /etc/init.d/nginx restart
