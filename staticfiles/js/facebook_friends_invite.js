/*
  A small class that allows normal backbone interaction with
  the abomination that is the facebook api
  No view included due to the individuality of each solution
  the properties for the model are: uid, name, pic_squar
*/
(function($){
   // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.FacebookFriend = Backbone.Model.extend({
	defaults: {
            highlighted_name: "",
	}
    });

    window.FacebookFriendsCollection = Backbone.Collection.extend({
	model:FacebookFriend,
        options: {
            page: 0,
            search: '',
            limit: 50,
        },

        url: '/fql',
	countFriendsQuery: function() {
	    var query = "SELECT friend_count FROM user WHERE uid = me()";
	},
        // Generate a query for the facebook open graph
        // this uses fql for pagination and searching of users
        query: function() {
            // Current users friends who are not on spling
            url = "SELECT uid, name, pic_square FROM user WHERE has_added_app=0 AND uid IN (SELECT uid2 FROM friend WHERE uid1 = me())";

            // Any search parameters
            /*if(this.options.search != '') {
              url += " AND strpos(lower(name), '#{@options.search.toLowerCase()}') >= 0";
              }*/

            // Pagination
            url += " ORDER BY name LIMIT " + this.options.limit + " OFFSET " + this.options.page * this.options.limit;
            return url
        },

        initialize: function(appId, app_token) {
            facebookAppId = '279761435376574';
            facebookDefaultScope = ["email", "user_birthday"];
            staticUrl = '/static/';
            FB.init({appId: facebookAppId, status: false, cookie: true, xfbml: true, oauth: true});
            // Initialize the facebook api
            /*FB.init
              appId : appId
              app_token : app_token
              status : true*/
        },

        // A custom fetch method that uses the facebook api
        // instead of backbones fetch()
        fetch: function(options) {
            options = options ? _.clone(options) : {};
            console.log('fql query', this.query());

            var collection = this;
            //var success = options.success;
            // This is the normal backbone behaviour
            // turn the response into models and call any
            // user defined success callbacks
            var success = function(resp) {
		console.log("options.success", collection.options.add);
                collection[collection.options.add ? 'add' : 'reset'](collection.parse(resp), collection.options);
                if (options.success) return options.success(collection, resp, options);
            }
            // Check the login status before calling the api
            // without this expect an api error
            var _this = this;
            FB.getLoginStatus( function(response) {
                if (response.status == 'connected') {
                    FB.api({
                        method: 'fql.query',
                        query: _this.query()}, success);
                }
                else {
                    // display error
                    console.log("not connected");
                }
            });
	    options.error = Backbone.wrapError(options.error, collection, options);
	    console.log("OPTIONS", options);
            return this
        },
        filterFriends: function(letters) {
            if(letters == "") return this;

	    letters_pattern = "(" + letters + ")";
            var pattern = new RegExp(letters_pattern,"i");
            return _(this.filter(function(data) {
		var name = data.get("name");
		if(!pattern.test(name)) return false;
		
		// add <span> around matched part of name, so we can  highlight it
		var highlighted_name = name.replace(pattern, '<span class="friend-name-highlighted">$1</span>');
		
		data.set({highlighted_name:highlighted_name, silent:true});
		return true;
            }));
        },
    });

    window.FacebookFriendListItemView = Backbone.View.extend({
        tagName:"li",
        className: "facebook-friend-item",
        template:_.template($('#tpl-facebook-friend-item').html()),
        initialize:function () {
            //_.bindAll(this, 'like_button_mousein', 'like_button_mouseout');
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
	    'click button': 'inviteFriend',
        },
	inviteFriend: function() {
	    console.log(this.model);
	    FB.ui({
		method: 'send',
		name: 'StyleMatch - för dig som frisör',
		link: 'http://www.stylematch.se',
		to: this.model.get('uid')
            });
	},
        close:function () {
            $(this.el).unbind();
            $(this.el).remove();
        }
    });

    window.InviteFriendsView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
	    _.bindAll(this, 'realInit', 'addAll', 'addOne');
            // need to wait for Facebook JS to be initialized
            window.fbAsyncInit = this.realInit;
        },
        realInit: function(){
            this.facebookFriendsList = new FacebookFriendsCollection();
            this.facebookFriendsList.bind('add', this.addOne, this);
            this.facebookFriendsList.bind('reset', this.addAll, this)
	    var _this = this;
            this.facebookFriendsList.fetch({
                success: function(collection, response) {
                    console.log("success.fetch",collection, response);
                    /*if(!response) {
                        var noty_id = noty({
                            text: 'Bilderna kunde inte hämtas!',
                            type: 'error'
                        });
                    }*/
		    console.log("fetch success");
		    //_this.addAll();
                },
                error: function() {
                    console.log("error fetch");
                }
            });
        },
        addOne: function(facebook_friend) {
	    $('.facebook-friends ul').append(new FacebookFriendListItemView({model:facebook_friend}).render().el);
        },
        addAll: function() {
	    var _this = this;
            _.each( this.facebookFriendsList.models, function (facebook_friend) {
                _this.addOne(facebook_friend);
            });
        },
	filterFriends: function(e) {
	    var _this = this;
	    var letters = $('#filter-friends').val();
	    $('.facebook-friends ul').html("");
	    
	    var filtered_friends = this.facebookFriendsList.filterFriends(letters);

	    // if no letters in search box, we dont want any highlighted letters
	    if(!letters) {
		console.log("addall filter",_this.facebookFriendsList.models );
		_.each( this.facebookFriendsList.models, function (facebook_friend) {
		    // if 'highlighted_name' variable on model is empty, the template
		    // will use 'name' instead
		    facebook_friend.set({highlighted_name:""});
                    _this.addOne(facebook_friend);
		});
	    } else {
		filtered_friends.each(function (facebook_friend) {
                    _this.addOne(facebook_friend);
		});

	    }

	},
        render:function (eventName) {
            return this;
        },
	events: {
	    'keyup #filter-friends': 'filterFriends',
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        }
    });
    this.InviteFriendsView = new InviteFriendsView();

})(jQuery);