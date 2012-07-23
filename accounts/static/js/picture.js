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
            "click .delete-image":"deleteImage",
            "click .show_image_on_profile":"switchDisplayOnProfile",
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
                        var noty_id = noty({
                            text: 'Kommentaren uppdaterad!',
                            type: 'success'
                        });
                    },
                    error:function() {
                        var noty_id = noty({
                            text: 'Kommentaren kunde inte uppdateras!',
                            type: 'error'
                        });
                    }
                });
            }
        },
        switchDisplayOnProfile: function() {
            var new_comment = $(this.el).find("textarea").val();
            new_comment = new_comment.replace(/\s+$/,''); //remove all trailing whitespaces
            var comment = this.model.get("comment");
            this.model.set({comment:new_comment, silent:true});

            var display_on_profile = this.model.get("display_on_profile");
            var bool = !display_on_profile;

            this.model.set({display_on_profile: bool, silent:true});

            this.model.save({}, {
                success:function () {
                        var noty_id = noty({
                            text: 'Uppdateringen lyckades!',
                            type: 'success'
                        });
                },
                error:function() {
                        var noty_id = noty({
                            text: 'Uppdateringen kunde inte slutföras!',
                            type: 'error'
                        });
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
                        var noty_id = noty({
                            text: 'Oops, något gick galet!',
                            type: 'error'
                        });
                    //console.log("Error: Model didnt sync with server, after the order was changed");
                }
            });
        },
        deleteImage:function () {
            var image = this;
            $.noty.closeAll();
            noty({
                text: "Är du säker på att du vill ta bort den här bilden?",
                buttons: [
                  {type: 'btn btn-success', text: 'Ja, ta bort den.', click: function($noty) {
                      image.model.destroy({
                          success:function() {
                          },
                          error:function() {
                              var noty_id = noty({
                                  text: "Bilden kunde inte tas bort. Kontrollera anslutningen!",
                                  type: 'error'
                              });
                          }
                      });
                      $noty.close();
                    }
                  },
                  {type: 'btn btn-danger', text: 'Nej, behåll den.', click: function($noty) {
                      $noty.close();
                    }
                  }
                  ],
                type: 'warning',
                closable: false,
                timeout: false,
                layout: 'center',
                animateOpen: {opacity: 'show'},
                animateClose: {opacity: 'hide'},
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
	    $('#image-type-info').popover({placement:'left', delay: { show: 500, hide: 100 }});
	    $('#image-theme-description-sup').popover({delay: { show: 500, hide: 100 }});

            this.serviceList = new ServiceCollection();

            this.serviceList.fetch({
                success: function(collection, response) {
                    if(!response) {
                        var noty_id = noty({
                            text: 'Bilderna kunde inte hämtas!',
                            type: 'error'
                        });
                    }
                    $('#image-list').html(new ServiceListView({model:collection}).render().el);
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
