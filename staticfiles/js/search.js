(function($){

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.Profile = Backbone.Model.extend({});

    window.ProfileCollection = Backbone.Collection.extend({
        model:Profile,
        // Set by the django template
        url: PROFILE_API_URL,
    });

    window.Map = Backbone.Model.extend({});

    window.MapView = Backbone.View.extend({
        el: $('#map_canvas'),
        model: Map,
        tagName: 'div',
        className:'map',
        latitude:'59.33',
        longitude:'18.07',
        maxZoom: 12, // maximum zoom achieved when refreshing the list

        initialize: function(opts) {

            this.profileList = opts.ProfileList;

            var myOptions = {
              mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            this.map = new google.maps.Map(this.el, myOptions);
            this.markerBounds = new google.maps.LatLngBounds();

            // add listener for the bounds. If the bounds are too small the zoom could be too high.
            // This prevents the zoom from going above this.maxZoom
            var self = this; // ``this`` will start pointing on the map
            google.maps.event.addListener(this.map, 'zoom_changed', function() {
                zoomChangeBoundsListener =
                    google.maps.event.addListener(self.map, 'bounds_changed', function(event) {
                        if (this.getZoom() > self.maxZoom && this.initialZoom == true) {
                            this.setZoom(self.maxZoom);
                            this.initialZoom = false;
                        }
                    google.maps.event.removeListener(zoomChangeBoundsListener);
                });
            });
            this.map.initialZoom = true;
            this.map.fitBounds(this.markerBounds);

            _.bindAll(this, 'render');
            this.render();
        },
        render: function() {
            // for some reason it didn't work passing ``this`` as a context
            // variable to the underscore method
            var self = this;

            var geocoder = new google.maps.Geocoder();

            _.each(this.profileList.models, function(profile) {

                // create an address string
                var address = profile.attributes.salon_adress + ' ' +
                              profile.attributes.zip_adress + ', ' +
                              profile.attributes.salon_city;

                // convert an address to a LatLng position and put a marker there
                geocoder.geocode({ 'address': address }, function(result, status) {
                    if (status === 'OK') {
                        // create a location
                        var loc = new google.maps.LatLng(result[0].geometry.location.lat(),
                                                         result[0].geometry.location.lng());

                        // extend the markerBounds
                        self.markerBounds.extend(loc);

                        // make sure the map fits all markers
                        self.map.fitBounds(self.markerBounds);

                        // Add the marker
                        var marker = new google.maps.Marker({
                            position: loc,
                            map: self.map,
                            title: profile.attributes.salon_name
                        });
                    }
                });
            });
            return this;
        }
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
        template: _.template($('#tpl-profile-list-item').html()),

        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
    });

    window.ProfileView = Backbone.View.extend({
        el: $("body"),
        initialize:function (opts) {
            this.profileList = new ProfileCollection();
            this.filter();
        },
        events:{
            "click .submit":"filter"
        },
        filter: function() {

            data = {};
            city = $('#city').val();
            if (city !== 'Alla') {
                data = { 'salon_city__iexact' : $('#city').val() };
            }
            data['limit'] = 0; // list ALL stylists
            this.profileList.fetch({
                data: data,
                success: function(collection, response) {
                    if(!response) {
                        var noty_id = noty({
                            text: 'Profilerna kunde inte hämtas!',
                            type: 'error'
                        });
                    }
                    var mapView = new MapView({ ProfileList: collection });
                    $('#profile-list').html(new ProfileListView({model:collection}).render().el);
                }
            });
        }
    });

    this.ProfileView = new ProfileView();

})(jQuery);
