(function($){
    // `Backbone.sync`: Overrides persistence storage with dummy function. This enables use of `Model.destroy()` without raising an error.
    /*Backbone.sync = function(method, model, success, error){
     success();
     }*/

    var List = Backbone.Collection.extend({
        url: '/api/service/'
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
            var self = this;
            this.model.bind("add", function (service) {
                $(self.el).append(new ServiceListItemView({model:service}).render().el);
            });
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

        initialize:function () {
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.close, this);
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
            "change input":"change",
            "click .save":"saveService",
	    "click .edit":"editService",
            "click .delete":"deleteService"
        },

        change:function (event) {
            var target = event.target;
            console.log('changing ' + target.id + ' from: ' + target.defaultValue + ' to: ' + target.value);
            // You could change your model on the spot, like this:
            // var change = {};
            // change[target.name] = target.value;
            // this.model.set(change);
        },
	editService:function () {
            console.log("edit");
	},
        saveService:function () {
            console.log("save");
            /*this.model.set({
             name:$('#name').val(),
             grapes:$('#grapes').val(),
             country:$('#country').val(),
             region:$('#region').val(),
             year:$('#year').val(),
             description:$('#description').val()
             });
             if (this.model.isNew()) {
             app.wineList.create(this.model);
             } else {
             this.model.save();
             }*/
            return false;
        },

        deleteService:function () {
            console.log("delete");
            this.model.destroy({
             success:function () {
             alert('Wine deleted successfully');
             window.history.back();
             }
             });
            return false;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).remove();
        }

    });

    window.ServiceView = Backbone.View.extend({

        //template:_.template($('#tpl-wine-details').html()),
        initialize:function () {
            this.model.bind("change", this.render, this);
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
            "change input":"change",
            "click .save":"saveWine",
            "click .delete":"deleteWine"
        },

        change:function (event) {
            var target = event.target;
            console.log('changing ' + target.id + ' from: ' + target.defaultValue + ' to: ' + target.value);
            // You could change your model on the spot, like this:
            // var change = {};
            // change[target.name] = target.value;
            // this.model.set(change);
        },

        saveWine:function () {
            console.log("save");
            /*this.model.set({
             name:$('#name').val(),
             grapes:$('#grapes').val(),
             country:$('#country').val(),
             region:$('#region').val(),
             year:$('#year').val(),
             description:$('#description').val()
             });
             if (this.model.isNew()) {
             app.wineList.create(this.model);
             } else {
             this.model.save();
             }*/
            return false;
        },

        deleteWine:function () {
            console.log("delete");
            /*this.model.destroy({
             success:function () {
             alert('Wine deleted successfully');
             window.history.back();
             }
             });*/
            return false;
        },

        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
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
