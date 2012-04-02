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

#Should be an if case here, so it's easy to install on MacOSX too
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

git submodule update
git submodule init

echo "Why do this manually? -> since source doesnt work in bash"
echo "TODO: Solve it"
echo "The script is now completed. Please type in: "
echo ""
echo "	cd ProjectX/"
echo "	source projectx/bin/activate"
echo "	pip install django-galleria/"
echo "	pip install -r requirements.txt"

# have syncdb initiate everything, and skip south for now
echo "  ./manage.py syncdb --al"

# initiate south
echo "  ./manage.py migrate --fake"
echo "  rm -rf django-galleria"
echo "  ./manage.py runserver_plus"
