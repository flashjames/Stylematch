(function($){

    window.Service = Backbone.Model.extend({});

    window.ServiceCollection = Backbone.Collection.extend({
        model:Service,
        // Set by the django template
        url: SERVICE_API_URL
    });

    window.ServiceListView = Backbone.View.extend({
        tagName:'ul',
        className: 'service-list',
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
        }
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
                     var noty_id = noty({
                         text: "Error: Model didnt sync with server, after the order was changed",
                         type: 'error'
                     });
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
            var service = this;
            jConfirm('Är du säker på att du vill ta bort den här behandlingen?',
                     'Bekräfta borttagning',
                 function(r) {
                    if (r === true) {
                        service.model.destroy({
                            success:function() {
                                vent.trigger('changeModelToEdit', new Service());
                            },
                            error:function() {
                                var noty_id = noty({
                                    text: "Behandlingen kunde inte tas bort. Kontrollera anslutningen!",
                                    type: 'error'
                                });
                            }
                        });
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
        events: {
            'click .new-service': 'newForm',
        },
        newForm: function() {
            vent.trigger("newForm", this.model);
            return false;
        },
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
            vent.bind("newForm", this.newForm);

            this.serviceList = new ServiceCollection();
            this.serviceListView = new ServiceListView({model:this.serviceList});

            this.newForm();
            var self = this;
            this.serviceList.fetch({
                success: function(collection, response) {
                    if(collection.size() > 0) {
                        self.showPriceList();
                    }

                    if(!response) {
                        var noty_id = noty({
                            text: "Error: Couldn't get users services from API",
                            type: 'error'
                        });
                    }
                },
                error: function(collection, error, options) {
                    var noty_id = noty({
                        text: "Connection Error",
                        type: 'error'
                    });
                }
            });
            $('#service-list').html(this.serviceListView.render().el);
        },
        showPriceList: function () {
            $('.edit-service-form-right').removeClass('hide-block');
        },
        events:{
            'click .save': 'formSave'
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

            var btn = $('.save');
            btn.html("Spara");
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        },
        formSave: function() {
            var ServiceView = this;

            // a callback used on both model.save() and serviceList.create()
            var self = this;
            responseCallback = {
                success: function(collection, error, options) {
                    var noty_id = noty({
                        text: 'Uppdateringen lyckades!',
                        type: 'success',
                    });
                    ServiceView.newForm();
                    self.showPriceList();
                },
		error: function(collection, error, options) {
		    //Some error in the user input
		    if(error.status == 400) {
			
			ServiceView.cleanForm();

			var btn = $('.save');
			btn.html("Spara");
			ServiceView.displayFormErrors(collection, error, options);
		    //The server probably went down 
		    } else {
                var noty_id = noty({
                    text: 'Uppdateringen misslyckades!',
                    type: 'error'
                });
			});
		    }
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
                //TODO: Log this somewhere?
                var noty_id = noty({
                    text: 'Det skedde ett fel och felmeddelandet var inte i korrekt JSON-format!',
                    type: 'error'
                });
            }
        }
    });

    //events used to delegate between views
    var vent = _.extend({}, Backbone.Events);
    this.ServiceView = new ServiceView();


})(jQuery);
