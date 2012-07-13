(function($){

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.Map = Backbone.Model.extend({});

    window.MapView = Backbone.View.extend({
        tagName: 'div',
        className:'map',
        latitude:'59.33',
        longitude:'18.07',

        initialize: function() {
            this.latlng = new google.maps.LatLng(this.latitude, this.longitude);

            var myOptions = {
              center: this.latlng,
              zoom: 14,
              mapTypeId: google.maps.MapTypeId.ROADMAP
            };

            this.map = new google.maps.Map(document.getElementById('map_canvas'), myOptions);

            _.bindAll(this, 'render');
            this.render();
        },
        render: function() {
            return this;
        }
    });


    window.Profile = Backbone.Model.extend({});

    window.ProfileCollection = Backbone.Collection.extend({
        model:Profile,
        // Set by the django template
        url: PROFILE_API_URL,
    });

    window.ProfileListView = Backbone.View.extend({
        tagName:'ul',
        className: 'profile-list',

        render:function (eventName) {
            // render each model object as a li object
            _.each(this.model.models, function (profile) {
                $(this.el).append(new ProfileListItemView({model:profile}).render().el);
            }, this);

            return this;
        },
    });

    window.ProfileListItemView = Backbone.View.extend({
        tagName:"li",
        className: "profile-list-item-city",
        template:_.template($('#tpl-profile-list-item').html()),

        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
    });

    window.ProfileView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {

            // Load profile with default values
            this.filter();
        },
        events:{
            "click .submit":"filter"/*,
            "change #city":"filter"*/
        },
        filter: function() {
            this.profileList = new ProfileCollection();

            data = {};
            city = $('#city').val();
            if (city !== 'Alla') {
                data = { 'salon_city__iexact' : $('#city').val() };
            }
            online_booking = $('#online-booking').prop("checked");
            if (online_booking === true) {
                data['show_booking_url'] = true;
            }
            this.profileList.fetch({
                data: data,
                success: function(collection, response) {
                    if(!response) {
                        var noty_id = noty({
                            text: 'Profilerna kunde inte hämtas!',
                            type: 'error'
                        });
                    }
                    $('#profile-list').html(new ProfileListView({model:collection}).render().el);
                }
            });
        }
    });

    this.ProfileView = new ProfileView();
    this.MapView = new MapView();


})(jQuery);
