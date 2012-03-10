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
#Get username
echo -n "Please input your username at github, finish by pressing [ENTER]: "
read username
		
#Init git-folder
git init
git clone http://$username@github.com/Jenso/ProjectX.git ProjectX
echo "Cloning is complete. You now have the repostory"

#Enter newly created folder
cd ProjectX/

#Install python dev and so on
sudo apt-get install python2.7 python-dev python-pip python-virtualenv


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
echo "	sudo pip install django-galleria/"
echo "	sudo pip install -r requirements.txt"
