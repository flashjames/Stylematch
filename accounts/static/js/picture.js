(function($){

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.Service = Backbone.Model.extend({});

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

            // always have six image boxes on the page
            var empty_image_list_item = $('#tpl-empty-image-list-item').html();

        // number of uploaded images
        var uploaded_images = this.model.size();

        // at least six "images"
        if(uploaded_images < 6) {
            for(i=uploaded_images;i<6;i++) {
                // dont add padding at bottom, if no uploaded images yet
                if(uploaded_images == 0) {
                    $(this.el).append($(empty_image_list_item).removeClass('empty-image-fixed-height'));
                } else {
                    $(this.el).append($(empty_image_list_item));
                }
            }
        }
        // always fill one row, and if the last row is filled, fill the next row too
        else {
            var s = uploaded_images % 3;
            for(i=s;i<3;i++) {
                $(this.el).append(empty_image_list_item);
            }
        }

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
                $(element).trigger('updateOrder');
            });
        },
        saveEachModel: function() {
            this.model.each(function(model) {

            });
        }
    });

    window.ServiceListItemView = Backbone.View.extend({
        tagName:"li",
        className: "image-block image-list-item",
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
            "click .delete-image":"deleteService",
            "click .show_image_on_profile":"switchDisplayOnProfile",
            "change .profile_image_radiobutton": "setProfileImage",
            "click .save": "saveComment"
        },
        saveComment: function() {
            var new_comment = $(this.el).find("textarea").val();
            new_comment = new_comment.replace(/\s+$/,''); //remove all trailing whitespaces
            var comment = this.model.get("comment");

            // comment have been changed
            if(new_comment != comment) {
                this.model.set({comment:new_comment, silent:true});

                this.model.save({}, {
                    success:function () {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Kommentaren uppdaterad!'
                        }, {
                            expires: 3000,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    },
                    error:function() {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Kommentaren kunde inte uppdateras!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    }
                });
            } else {
                //do nothing
            }
        },
        switchDisplayOnProfile: function() {
            var display_on_profile = this.model.get("display_on_profile");
            //console.log(display_on_profile, this.model);
            var bool;
            if(display_on_profile)
                bool = false;
            else
                bool = true;

            this.model.set({display_on_profile: bool, silent:true});

            this.model.save({}, {
                success:function () {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Uppdateringen lyckades!'
                        }, {
                            expires: 2000,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                },
                error:function() {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Uppdateringen kunde inte slutföras!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                }
            });
        },
        setProfileImage: function(e) {

            // FIXME: radiobuttons are weird when using model.set({...}) followed by
            // save() since they force re-rendering or something alike.
            // Current solution is to do set and save in same operation...
            this.model.save({image_type: 'C'}, {
                        silent : true,
                        success : function () {
                            // TODO: Add dialog in interface
                            //console.log('setProfileImage successfully changed');
                        },
                        error : function() {
                            // TODO: Add dialog in interface
                            //console.log('setProfileImage saving failed!');
                        }
            });
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
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Oops, något gick galet!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    //console.log("Error: Model didnt sync with server, after the order was changed");
                }
            });
            //console.log("na", $(this.el).index(), this.model);
        },
        deleteService:function () {
            this.model.destroy({
                success:function () {
                    // TODO: Add dialog in interface
                    //console.log('Picture deleted successfully');
                },
                error:function() {
                    $('#alert').notify();
                    $('#alert').notify("create", {
                          text: 'Bilden kunde inte tas bort!'
                    }, {
                        expires: false,
                        click: function(e,instance) {
                            instance.close();
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

    window.ServiceView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
            //Glue code, that initialize's all views and models

            //_.bindAll(this, "formSave", "changeModelToEdit", "displayFormErrors");
            //vent.bind("changeModelToEdit", this.changeModelToEdit);

            this.serviceList = new ServiceCollection();

            this.serviceList.fetch({
                success: function(collection, response) {
                    if(!response) {
                        $('#alert').notify();
                        $('#alert').notify("create", {
                              text: 'Bilderna kunde inte hämtas!'
                        }, {
                            expires: false,
                            click: function(e,instance) {
                                instance.close();
                            }
                        });
                    }
                    $('#image-list').html(new ServiceListView({model:collection}).render().el);
                    //console.log("fetch()",response);
                }
            });
        this.initGalleryUploadDialog();
        this.initProfileImageUploadDialog();
        },
        events:{
        },
    initGalleryUploadDialog: function() {
        var current_modal = $('#image-upload-dialog-gallery');
        current_modal.modal({show:false});
        $(".empty-image-list-item").live('click', function() {
                current_modal.modal('show');
            });
        },
    initProfileImageUploadDialog: function() {
        var current_modal = $('#image-upload-dialog-profileimage');
        current_modal.modal({show:false});
        $(".profile-image-edit").live('click', function() {
                current_modal.modal('show');
            });
        },

        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        }
    });

    this.ServiceView = new ServiceView();


})(jQuery);
