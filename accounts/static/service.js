(function($){
    // `Backbone.sync`: Overrides persistence storage with dummy function. This enables use of `Model.destroy()` without raising an error.
    /*Backbone.sync = function(method, model, success, error){
     success();
     }*/

    var List = Backbone.Collection.extend({
        url: '/api/service/',
    });

    // Models
    window.Service = Backbone.Model.extend();

    window.ServiceCollection = Backbone.Collection.extend({
        model:Service,
        url:"/api/service/?format=json"
    });

    // Views
    window.ServiceListView = Backbone.View.extend({

        tagName:'ul',

        initialize:function () {
            this.model.bind("reset", this.render, this);
        },

        render:function (eventName) {
            _.each(this.model.models, function (service) {
                $(this.el).append(new ServiceListItemView({model:service}).render().el);
            }, this);
            return this;
        }

    });

    window.ServiceListItemView = Backbone.View.extend({

        tagName:"li",

        template:_.template($('#tpl-service-list-item').html()),

        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        }

    });

    window.ServiceView = Backbone.View.extend({

        //template:_.template($('#tpl-wine-details').html()),

        render:function (eventName) {
            //$(this.el).html(this.template(this.model.toJSON()));
            return this;
        }

    });

    function init() {
        this.serviceList = new ServiceCollection();
        this.serviceListView = new ServiceListView({model:this.serviceList});
        this.serviceList.fetch();
        $('#service-list').html(this.serviceListView.render().el);
    }
    init();


})(jQuery);
