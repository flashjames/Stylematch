(function($){

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.FeaturedProfile = Backbone.Model.extend({});

    window.ProfileCollection = Backbone.Collection.extend({
        model:FeaturedProfile,
        // Set by the django template
        url: FEATURED_PROFILE_API_URL,
    });

    window.ProfileListView = Backbone.View.extend({
        tagName:'div',
        className: 'featured-profile-list row',

        render:function (eventName) {
            // render each model object as a div object
            _.each(this.model.models, function (profile) {
                $(this.el).append(new ProfileListItemView({model:profile}).render().el);
            }, this);

            return this;
        },
    });

    window.ProfileListItemView = Backbone.View.extend({
        tagName:"div",
        className: "featured-profile-list-item span3",
        template:_.template($('#tpl-featured-profile-list-item').html()),

        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
    });

    window.ProfileView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
            //Glue code, that initialize's all views and models

            this.profileList = new ProfileCollection();

            data = { 'salon_city__iexact' : $('#city').val() };
            this.profileList.fetch({
                data: data,
                success: function(collection, response) {
                    if(!response) {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Profilerna kunde inte hämtas!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    }
                    $('#featured-profile-list').html(new ProfileListView({model:collection}).render().el);
                }
            });
        },
        events:{
            "change #city":"filter"
        },
        filter: function() {
            this.profileList = new ProfileCollection();

            data = { 'salon_city__iexact' : $('#city').val() };
            this.profileList.fetch({
                data: data,
                success: function(collection, response) {
                    if(!response) {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Profilerna kunde inte hämtas!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    }
                    $('#featured-profile-list').html(new ProfileListView({model:collection}).render().el);
                }
            });
        }
    });

    this.ProfileView = new ProfileView();


})(jQuery);
