(function($){

    window.Service = Backbone.Model.extend({});

    window.ServiceCollection = Backbone.Collection.extend({
        model:Service,
	// TODO: Let django set this url? Instead of hardcoding it.
        url:"/api/service/"
    });

    window.ServiceListView = Backbone.View.extend({
        tagName:'ul',
	id: 'service-list',
        initialize:function () {
	    // TODO: change this.model to be this.collection
	    // since this.model is currently a collection.
	    // would that break anything?

	    _.bindAll(this, 'updateOrder', 'saveEachModel');
            this.model.bind('reset', this.render, this);
            var self = this;
            this.model.bind('add', function (service) {
                $(self.el).append(new ServiceListItemView({model:service}).render().el);
            });
        },
        render:function (eventName) {
	    // render each model object as a li object
            _.each(this.model.models, function (service) {
                $(this.el).append(new ServiceListItemView({model:service}).render().el);
            }, this);

	    var self = this;
	    // make the ul list sortable with the function sortable() from jquery ui
	    $(this.el).sortable({
		items: 'li', 
		//when a object have changed position, update the backbone models order field 
		update: function() { 
		    self.updateOrder();
		}
	    });

            return this;
        },
	updateOrder: function() {
	    /*
	     * Trigger update order of each Service model item
	     * Need to trigger it on ServiceListItemView that hold's the model
	     * since we need to access the li's index in the <ul> list
	     */
	    $(this.el).children("li").each(function(index, element) {
		$(element).trigger('updateOrder');
	    });
	},
	saveEachModel: function() {
	    this.model.each(function(model) {
		console.log(model);
	    });
	},
    });

    window.ServiceListItemView = Backbone.View.extend({
        tagName:"li",
        template:_.template($('#tpl-service-list-item').html()),

        initialize:function () {
	    _.bindAll(this, "updateModelOrder");
	    $(this.el).bind('updateOrder', this.updateModelOrder);
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.close, this);
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
            "click .edit":"editService",
            "click .delete":"deleteService"
        },
	updateModelOrder: function() {
	    /*
	     * Update the Service objects order field according to order in the <ul> list 
	     */
	    var indexInList = $(this.el).index();
	    // silent => dont want to rerender the view
	    this.model.set({order: indexInList, silent:true});
	    this.model.save({}, {
		 error: function(collection, error, options) {
		     console.log("Error: Model didnt sync with server, after the order was changed");
		 }
	    });
	    //console.log("na", $(this.el).index(), this.model);
	},
        editService:function () {
            /* Create bi-directional binding between the HTML form input elements
             * and the model for this Item
             */
            vent.trigger("changeModelToEdit", this.model);
        },
        deleteService:function () {
            this.model.destroy({
                success:function () {
		    // TODO: Add dialog in interface
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
	    //Glue code, that initialize's all views and models
	    
            _.bindAll(this, "formSave", "changeModelToEdit", "displayFormErrors");
            vent.bind("changeModelToEdit", this.changeModelToEdit);

            this.serviceList = new ServiceCollection();
            this.serviceListView = new ServiceListView({model:this.serviceList});

            this.newForm();
	    
            this.serviceList.fetch({
                success: function(collection, response) {
                    if(!response)
                        //TODO: Display error message "couldnt get views"
                        console.log("Error: Couldnt get user's services from API");
                }
            });
            $('#service-list').html(this.serviceListView.render().el);
        },
	events:{
            'click .save': 'formSave',
	    'click .new-service': 'newForm'
        },
        newForm: function() {
            this.model = new Service();
            this.FormView = new FormView({model: this.model});
        },
	cleanForm: function() {
	    this.FormView = new FormView({model: this.model});
	},
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        changeModelToEdit: function(model) {
            this.model = model;
            this.FormView = new FormView({model:model});
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        },
        formSave: function() {
	    var ServiceView = this;
	    
	    // a callback used on both model.save() and serviceList.create()
	    responseCallback = {
		success: function(collection, error, options) {
		    ServiceView.newForm();
		},
		error: function(collection, error, options) {
		    ServiceView.cleanForm();
		    ServiceView.displayFormErrors(collection, error, options);
		}
	    };

	    // if it's a model that's not synced to the server and not in the 
	    // services list yet, on the page -> collection.create()
	    if(this.model.isNew())
		this.serviceList.create(this.model, responseCallback);
	    // already on server, just sync it.
	    else
		this.model.save({}, responseCallback);

            return false;
        },
        displayFormErrors: function(collection, error, options) {
	    
	    // error, this is a jqXHR object (jquery ajax object)
	    // http://api.jquery.com/jQuery.ajax/#jqXHR
	    
	    // convert the responsetext that's a string with json data
	    // to a usable object
	    try {
		// ugly hack to convert to json object, the other way around
		// tho, is to go change in the Backbone framework code
		// http://coded-codes101.blogspot.se/2011/07/jquery-ajax-error-function.html
		eval("var errorResponseJSON = " + error.responseText + ";");
		for( var field in errorResponseJSON) {
		    // get the help-inline dom object for the field
		    var control_group = $("#" + field).closest(".control-group");
		    control_group.addClass("error");

		    // display error message for field
		    var help_inline = control_group.find(".help-inline");
		    help_inline.text(errorResponseJSON[field][0]);
		}	
	    }
	    catch(err) {
		// TODO: Display error message somewhere better
		console.log("ERROR: The error message response wasnt a JSON object");
	    }
        }
    });

    //events used to delegate between views
    var vent = _.extend({}, Backbone.Events);
    this.ServiceView = new ServiceView();


})(jQuery);
