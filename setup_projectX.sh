
if [ "$0" != "bash" ]; then
    # We need to run the setup script in same context as the terminal.
    # This is done by using 'source' and an effect of this is $0 is set to 'bash' 
    # since it is essentially executed in the root bash process.  

    echo "Error! You need to use following syntax:"
    echo "source setup_projectX.sh"
    echo
    # if you're on ssh, this line will disconnect you from ssh
    #exit 1
fi

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


#git clone git@github.com:Jenso/ProjectX.git

#cd ProjectX/

echo "Fetching Django-Galleria"
git clone http://github.com/andrewebdev/django-galleria.git


echo "Now initializing django-enviroment"
virtualenv --no-site-packages projectx
source projectx/bin/activate

cd django-galleria/

# install modules that's downloaded with git, currently just galleria
git submodule init
git submodule update

echo "PWD: ", $PWD


cd ../

source projectx/bin/activate
pip install django-galleria/
pip install -r requirements.txt


# have syncdb initiate everything, and skip south for now
./manage.py syncdb --al

