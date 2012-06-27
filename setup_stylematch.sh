# Setup script for StyleMatch

echo "Welcome to setup script for StyleMatch."
echo "---------------------------------------"
echo

function setup()
{
    # Check for the Linux distribution and act accordingly.
    if [ "${OS}" = "Linux" ] ; then
            if [ -f /etc/redhat-release ] ; then
                    DIST='RedHat'
            elif [ -f /etc/SuSE-release ] ; then
                    DIST=`cat /etc/SuSE-release | tr "\n" ' '| sed s/VERSION.*//`
                    BAIL=true
            elif [ -f /etc/mandrake-release ] ; then
                    DIST='Mandrake'
                    BAIL=true
            elif [ -f /etc/debian_version ] ; then
                    DIST="Debian"
            fi
    else
        DIST='Not supported'
        BAIL=true
        echo "Sorry, other OS than Linux is not supported yet."
        echo "Please install manually"
        echo
    fi

    if [ ${BAIL} ] ; then
        echo "Sorry, your Linux distribution is not supported/tested yet."
        echo "Please install manually"
        echo
    else

        # Install needed programs
        if [ ${DIST} = 'Debian' ] ; then
            sudo apt-get install python python-dev python-pip python-virtualenv \
                                 python-virtualenvwrapper python-imaging libjpeg62-dev \
                                 gcc
        elif [ ${DIST} = 'RedHat' ] ; then
            sudo yum install python python-devel python-pip python-virtualenv \
                             python-virtualenvwrapper python-imaging libjpeg-devel \
                             gcc
        fi

        # Load the virtualenvwrapper if it wasn't already installed
        if [ !$WORKON_HOME ] ; then
            echo 'export WORKON_HOME=$HOME/.venvs' >> ~/.bash_profile
            echo 'source /usr/bin/virtualenvwrapper.sh' >> ~/.bash_profile
            export WORKON_HOME=$HOME/.venvs
            source /usr/bin/virtualenvwrapper.sh
        fi

        # Create virtualenv and activate it
        mkvirtualenv stylematch
        workon stylematch

        # Clone the repository
        git init
        git remote add origin git@github.com:Jenso/ProjectX.git
        git fetch origin
        git checkout master

        # Install submodules
        git submodule init
        git submodule update

        # Install requirements
        pip install -r requirements.txt

        # Create a local settings file
        echo 'from .dev import *' > settings/local.py

        # have syncdb initiate everything, and skip south for now
        python manage.py syncdb --al
    fi
}

OS=`uname -s`
if [ "${0}" != "/bin/bash" ] ; then
    # We need to run the setup script in same context as the terminal.
    # This is done by using 'source' and an effect of this is $0 is set to 'bash' 
    # since it is essentially executed in the root bash process.  

    echo "You need to use following syntax:"
    echo "source setup_stylematch.sh"
    echo
    # if you're on ssh, this line will disconnect you from ssh
    exit 1
else
    setup
fi

