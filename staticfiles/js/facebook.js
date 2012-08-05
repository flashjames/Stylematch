// http://stackoverflow.com/questions/3548493/how-to-detect-when-facebooks-fb-init-is-complete
function fbEnsureInit(callback) {
    if(!window.fbApiInit) {
        setTimeout(function() {fbEnsureInit(callback);}, 50);
    } else {
        if(callback) {
            callback();
        }
    }
}

facebookClass = function() {};
facebookClass.prototype = {
    connect: function () {
        this.connectLoading('En facebook pop-up har öppnats, följ instruktionerna för att logga in.');
        var _this = this;
        FB.login(function(response) {
            if (response.authResponse) {
                _this.connectLoading('Laddar din profil...');
                window.location = authenticationUrl +
                    '?access_token=' + response.authResponse.accessToken +
                    '&expires=' + response.authResponse.expiresIn +
                    '&signed_request=' + response.authResponse.signedRequest;
            }
            if (response.status == 'unknown') {
                var errorMessage = 'Vi kunde inte logga in dig. Var vänlig försök igen eller skapa ett konto manuellt.';
                _this.connectLoading(errorMessage, true, true);
            } else {
                //showloading
                _this.connectLoading('Laddar din profil...');
            }
        }, {scope: 'email'});
    },
    connectLoading: function (message, closeable, hideLoading) {
        /*
         * Show a loading lightbox to clarify what's happening to the user
         */
        var facebookMessage = document.getElementById('facebook_message');
        var facebookContainer = document.getElementById('facebook_container');
        if (!facebookMessage) {
            var container = document.createElement('div');
            container.id = 'facebook_container';
            var html = '<div id="facebook_shade" onclick="document.getElementById(\'facebook_container\').style.display=\'none\';"></div>\
<div id="facebook_wrapper">\
<div id="facebook_lightbox">\
<div id="facebook_message" />{{ message }}</div>\
<img id="facebook_loading" src="' + staticUrl + 'img/facebook_loading.gif" alt="..."/>\
<div id="facebook_close" style="display: none" onclick="document.getElementById(\'facebook_container\').style.display=\'none\';"></div>\
</div>\
</div>';
            html = html.replace('{{ message }}', message);
            container.innerHTML = html;
            document.body.appendChild(container);
            facebookMessage = document.getElementById('facebook_message');
            facebookContainer = document.getElementById('facebook_container');
        }
        facebookMessage.innerHTML = message;
        facebookContainer.style.display = message ? 'block' : 'none';
        document.getElementById('facebook_close').style.display = closeable ? 'block' : 'none';
        document.getElementById('facebook_loading').style.display = hideLoading ? 'none' : 'inline';

        //set the correct top
        var requiredTop = this.getViewportScrollY();
        document.getElementById('facebook_lightbox').style.top = requiredTop + 'px';
    },
    getViewportScrollY: function() {
        var scrollY = 0;
        if( document.documentElement && document.documentElement.scrollTop ) {
            scrollY = document.documentElement.scrollTop;
        }
        else if( document.body && document.body.scrollTop ) {
            scrollY = document.body.scrollTop;
        }
        else if( window.pageYOffset ) {
            scrollY = window.pageYOffset;
        }
        else if( window.scrollY ) {
            scrollY = window.scrollY;
        }
        return scrollY;
    }
};