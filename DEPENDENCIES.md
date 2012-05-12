##Client Side
###Backbone
Structure up javascript code.
Used on edit services page
###Underscore
Backbone dependency
###Backbone Modelbinding
Used on edit services page, mirrors models with the form.
###Twitter Bootstrap
CSS and Javscript bootstrap/framework

###JQuery
##Galleria
Used for the image gallery on the display profile page.

###Backbone Tastypie
A small conversion layer to make backbone.js and django-tastypie work together happily.
https://github.com/PaulUithol/backbone-tastypie

Used on edit services page. But will be used where ever the REST-api (django-tastypie) and Backbone will be used.

##Server Side

###Django Tastypie
###Django Registration
###Django Social Auth
###Django Braces
Reusable, generic mixins for Django class based views
https://github.com/brack3t/django-braces
Most used - LoginRequiredMixin
###Django Annoying
###Pillow
###Django Galleria
Used this stub to install Galleria in Django (not really needed?)
Mostly gives TEMPLATE_CONTEXT_VARIABLES
https://github.com/andrewebdev/django-galleria
Is it possible to add this to the requirements file, so it's 
downloaded with pip even though it's not in PIP's catalogue. 
I.e. download it from github and auto install.

###Django-SES
Send mail through Amazon SES
###Django default site
https://github.com/oppianmatt/django-defaultsite
Adds:
SITE_DOMAIN: The domain to use to replace 'example.com'. Defaults to your machine's hostname.
SITE_NAME: The sites name. Defaults to 'defaultsite'.

To settings.py
###Django-su
Adds possibility to login as another user on admin interface.
https://github.com/continuous/django-su

##Dev tools - Server Side
###South
###Werkzeug
###Django Debug Toolbar
###Commonware
###Django Extensions

## Dependencies on production server
###node.js
http://blog.marcqualie.com/2011/11/installing-nodejs-on-ubuntu-1110.html
###less
npm -g install less

Configure 
1. Create one .less file and then import other .less files into it.
2. If you have style.less , please put it as style.css in {% compress css %}, Benefit - instead of importing those css files in compiled version individually, it actually imports them into the main file thus faster page load time.
3. Use the less.js file to render all the less css in development environment (or if you are using Mac, use Less app)
4. Install node.js, npm and less on your server
5. In your deploy script (Fabric for me), put the command to compile .less into .css (if you did not use Less app in step 3)
