(function($){

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.InspirationImage = Backbone.Model.extend({});

    window.InspirationCollection = Backbone.Collection.extend({
        model:InspirationImage,
        // Set by the django template
        url: INSPIRATION_API_URL,
    });

    window.InspirationListView = Backbone.View.extend({
        tagName:'ul',
        className: 'inspiration-list',
        initialize:function () {
        },
        render:function (eventName) {
	    var first_inspiration_image = true;
            // render each model object as a li object
            _.each(this.model.models, function (inspiration_image) {
		inspiration_image.set({first_inspiration_image: false}, {silent: true});
		if(first_inspiration_image) {
		    inspiration_image.set({first_inspiration_image: true}, {silent: true});
		    first_inspiration_image = false;
		}
                $(this.el).append(new InspirationListItemView({model:inspiration_image}).render().el);
            }, this);

            return this;
        },
    });

    window.InspirationListItemView = Backbone.View.extend({
        tagName:"li",
        className: "inspiration-item",
        template:_.template($('#tpl-inspiration-image-list-item').html()),

        initialize:function () {
            //_.bindAll(this, "updateModelOrder");
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        events:{
	    "click .hype-button": "like"
        },
	like: function() {
	    /* Send likes for this Inspiration image to django and update the <p> object 
	       with number of likes */
	    var self = this;
	    $.post(
		'/like/',
		{ 'id': this.model.get('id'),
		  'csrfmiddlewaretoken': CSRF_TOKEN },
		function(data) {
		    var counter_p = $(self.el).find('.counter > p')
		    var number_of_votes = parseInt(counter_p.text());
		    if(data > number_of_votes) {
			counter_p.text(parseInt(counter_p.text()) + 1);
		    } else {
			// display that you've already liked the image
			// or that something have gone wrong
		    }
		}
	    );
 
	},
        close:function () {
            $(this.el).unbind();
            $(this.el).remove();
        }

    });

    window.InspirationView = Backbone.View.extend({
        el: $("body"),
        initialize:function () {
            //Glue code, that initialize's all views and models
            this.inspirationList = new InspirationCollection();
            this.inspirationList.fetch({
                success: function(collection, response) {
                    if(!response) {
                        var noty_id = noty({
                            text: 'Något gick fel, inga bilder kunde hämtas!',
                            type: 'error'
                        });
                    }
                    $('#inspiration-list').html(new InspirationListView({model:collection}).render().el);
                }
            });
        },
        events:{
        },
        render:function (eventName) {
            return this;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        }
    });
    this.InspirationView = new InspirationView();


})(jQuery);
