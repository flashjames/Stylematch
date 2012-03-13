clear
echo "Setting up enviroment for Project X development"
echo "-----------------------------------------------"
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""

#Install python dev and so on
sudo apt-get install python python-dev python-pip python-virtualenv python-imaging libjpeg62-dev


echo "Now initializing django-enviroment"
virtualenv --no-site-packages projectx
source projectx/bin/activate

echo "Fetching Django-Galleria"
git clone http://github.com/andrewebdev/django-galleria.git


cd django-galleria/
git submodule update
git submodule init

cd ..


echo "The script is now completed. Please type in: "
echo ""
echo "	cd ProjectX/"
echo "	source projectx/bin/activate"
echo "	pip install django-galleria/"
echo "	pip install -r requirements.txt"
echo "  ./manage.py syncdb"

# the --fake is needed since, the module fileupload and accounts are under south control
# -> if we just do migrate (which is part of south) it will wine that the tables already is created

echo "  ./manage.py migrate fileupload 0001 --fake"
echo "  ./manage.py migrate accounts 0001 --fake"
echo "  ./manage.py migrate"
echo "  rm -rf django-galleria"
echo "  ./manage.py runserver_plus"