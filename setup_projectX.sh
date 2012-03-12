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
sudo apt-get install python2.7 python-dev python-pip python-virtualenv libjpeg62-dev


echo "Now initializing django-enviroment"
virtualenv --no-site-packages projectx
source projectx/bin/activate

echo "Fetching Django-Galleria"
git clone http://github.com/andrewebdev/django-galleria.git

echo "Fetching jQuery-File-Upload"
git clone http://github.com/blueimp/jQuery-File-Upload.git

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
