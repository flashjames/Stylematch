
(function($){


    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.InspirationImage = Backbone.Model.extend({
        defaults: {
            first_inspiration_image: false
        }
    });

    window.InspirationCollection = Backbone.Paginator.requestPager.extend({
        model:InspirationImage,
        paginator_core: {
            // the type of the request (GET by default)
            type: 'GET',

            // the type of reply (jsonp by default)
            dataType: 'jsonp',

            // the URL (or base URL) for the service
            // Set by the django template
            url: INSPIRATION_API_URL,
        },
        paginator_ui: {
            // the lowest page index your API allows to be accessed
            firstPage: 0,

            // which page should the paginator start from
            // (also, the actual page the paginator is on)
            currentPage: 0,

            // how many items per page should be shown
            perPage: 10,

            // a default number of total pages to query in case the API or
            // service you are using does not support providing the total
            // number of pages for us.
            // 10 as a default in case your service doesn't return the total
            totalPages: 10
        },
        server_api: {
            // number of items to return per request/page
            'limit': function() { return this.perPage },

            // how many results the request should skip ahead to
            'offset': function() { return this.currentPage * this.perPage },
        },
        parse: function (response) {
            // Be sure to change this based on how your results
            // are structured (e.g d.results is Netflix specific)
            var tags = response.objects;

            // number of pages with content
            this.totalPages = Math.floor((response.meta.total_count - 1) / this.perPage);
            return tags;
        }
    });

    window.InspirationListItemView = Backbone.View.extend({
        tagName:"li",
        className: "inspiration-item",
        template:_.template($('#tpl-inspiration-image-list-item').html()),
        initialize:function () {
            _.bindAll(this, 'like_button_mousein', 'like_button_mouseout');
        },
        render:function (eventName) {
            $(this.el).html(this.template(this.model.toJSON()));


            // make lightbox work for the newly created image
            var image_a = $(this.el).find("a.inspiration-images");
            image_a.colorbox({rel:'group2', transition:"none", width:"75%", height:"90%"});

            // bind on
            this.$('.like-button').hover(this.like_button_mousein, this.like_button_mouseout);

            return this;
        },
        events:{
            "click .like-button": "like"
        },
        like_button_mousein: function() {
                var counter_p = this.$('.counter > p');
                this.number_of_votes = parseInt(counter_p.text());
                counter_p.text("+1");
        },
        like_button_mouseout: function() {
                var counter_p = this.$('.counter > p');
                counter_p.text(this.number_of_votes);
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
                    if(data > self.number_of_votes) {
                        counter_p.text(self.number_of_votes + 1);
			self.number_of_votes += 1;
                    } else {
                        // display that you've already liked the image
                        // or that something have gone wrong
			var noty_id = noty({
			    text: 'Du har redan gillat denna bild',
			    type: 'error'
			});
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
            this.inspirationList.bind('add', this.addOne, this);
            this.inspirationList.bind('reset', this.addAll, this);
	    _.bindAll(this, 'loadData', 'fetchSuccess'); 
	    
	    this.waitingForData = true;
            this.inspirationList.pager({error: this.fetchError, success: this.fetchSuccess});

	    // 'Body' won't trigger scroll events unless its overflow setting is explicitly set to 'scroll'
            $(window).bind('scroll', this.loadData);

        },
        fetchSuccess: function(collection, response) {
	    // no more pages of images to retrieve
	    if(collection.currentPage == collection.totalPages) {
		// used to dont trigger loadData, if set to true
		this.noPagesLeft = true;
	    }
            if(!response) {
                var noty_id = noty({
                    text: 'Ett okänt fel uppstod.!',
                    type: 'error'
                });
            } else {
		this.waitingForData = false;
		$('#loading-animation').hide(0);
	    }
        },
        fetchError: function(collection, response) {
            var noty_id = noty({
                text: 'Inga fler bilder kunde hämtas!',
                type: 'error'
            });
        },
        addOne: function(inspiration_image) {
            this.$('#inspiration-list').append(new InspirationListItemView({model:inspiration_image}).render().el);
        },
        addAll: function() {
            var first_inspiration_image = true;
            // render each model object as a li object
            _.each( this.inspirationList.models, function (inspiration_image) {
                // no <hr> before first image (is set in template, with first_inspiration_image)
                if(first_inspiration_image) {
                    inspiration_image.set({first_inspiration_image: true}, {silent: true});
                    first_inspiration_image = false;
                }
                this.$('#inspiration-list').append(new InspirationListItemView({model:inspiration_image}).render().el);
            }, this);
            return this;
        },
        loadData: function() {
	    // load more images three 'browser windows' from bottom
	    var triggerPoint = $(window).height() * 3;
	    
	    // dont load more images if already waiting for data or there are no more images to load
            if ( (this.el.scrollTop + triggerPoint > this.el.scrollHeight) && !this.waitingForData
	       && !this.noPagesLeft) {
 		this.waitingForData = true;
		$('#loading-animation').show(0);
		this.inspirationList.requestNextPage({error: this.fetchError, success: this.fetchSuccess, add: true });
            }
	    
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

