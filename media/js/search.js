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
        className: "profile-list-item",
        template:_.template($('#tpl-profile-list-item').html()),

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

            this.profileList.fetch({
                success: function(collection, response) {
                    console.log(collection);
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
                    $('#profile-list').html(new ProfileListView({model:collection}).render().el);
                }
            });
        },
    });

    this.ProfileView = new ProfileView();


})(jQuery);
