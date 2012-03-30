(function($){
   
    // Models
    window.Service = Backbone.Model.extend();

    window.ServiceCollection = Backbone.Collection.extend({
        model:Service,
        url:"/api/service/"
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
	    _.bindAll(this, "saveService");
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.close, this);
	    vent.bind("saveServices", this.saveService);
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
            /* Create bi-directional binding between the HTML form input elements
             * and the model for this Item
             * */
            vent.trigger("changeModelToEdit", this.model);
        },
        saveService:function () {
            this.model.save();
            return false;
        },
        deleteService:function () {
            this.model.destroy({
                success:function () {
                    console.log('Service deleted successfully');
                }
            });
            return false;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).remove();
        }

    });
    FormView = Backbone.View.extend({
        el: "#form",
	template:_.template($('#tpl-service-edit-form').html()),

        initialize: function(){
            /* Uses Backbone.ModelBinding */
	    $(this.el).html(this.template);
	    Backbone.ModelBinding.bind(this);
        },
        close: function(){
            // Model Unbinding
            this.remove();
            this.unbind();
            Backbone.ModelBinding.unbind(this);
        }
    });
    window.ServiceView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
            vent.bind("changeModelToEdit", this.changeModelToEdit);

            this.serviceList = new ServiceCollection();
            this.serviceListView = new ServiceListView({model:this.serviceList});
	    
	    this.FormView = new FormView({model:new Service()});


            this.serviceList.fetch({
                success: function(collection, response) {
                    if(!response)
                        //TODO: Display error message "couldnt get views"
                        console.log("Error: Couldnt get user's services from API");
                }
            });
            $('#service-list').html(this.serviceListView.render().el);
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
	    'click .save': 'formSave'
        },
        changeModelToEdit: function(model) {
	    this.currentModel = model;
            this.FormView = new FormView({model:model});
        },
        change:function (event) {
            var target = event.target;
            console.log('changing ' + target.id + ' from: ' + target.defaultValue + ' to: ' + target.value);
            // You could change your model on the spot, like this:
            // var change = {};
            // change[target.name] = target.value;
            // this.model.set(change);
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        },
	formSave: function() {
	    console.log("save");
	    //this.serviceList.add(this.FormView);
	    vent.trigger("saveServices", this.model);
	    return false;
	}

    });

    //events used to delegate between views
    var vent = _.extend({}, Backbone.Events);
    this.ServiceView = new ServiceView();


})(jQuery);
