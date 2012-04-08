(function($){

    window.Service = Backbone.Model.extend({
	
    });

    window.ServiceCollection = Backbone.Collection.extend({
        model:Service,
	// Set by the django template
        url: PICTURE_API_URL,
	});

    window.ServiceListView = Backbone.View.extend({
        tagName:'ul',
	className: 'image-list-horizontal',
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
		scrollSensitivity: 2,
		tolerance: 'pointer', // if this is not set, the reordering wont work properly
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
		console.log("asd");
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
	className: "image-block",
        template:_.template($('#tpl-image-list-item').html()),

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

    window.ServiceView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
	    //Glue code, that initialize's all views and models
	    
            //_.bindAll(this, "formSave", "changeModelToEdit", "displayFormErrors");
            //vent.bind("changeModelToEdit", this.changeModelToEdit);

            this.serviceList = new ServiceCollection();
            this.serviceListView = new ServiceListView({model:this.serviceList});

            //this.newForm();
	    
            this.serviceList.fetch({
                success: function(collection, response) {
                    if(!response)
                        //TODO: Display error message "couldnt get views"
                        console.log("Error: Couldnt get user's services from API");
		    console.log("fetch()",response);
                }
            });
	    
            $('#image-list').html(this.serviceListView.render().el);
        },
	events:{
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        },
    });

    //events used to delegate between views
    var vent = _.extend({}, Backbone.Events);
    this.ServiceView = new ServiceView();


})(jQuery);
