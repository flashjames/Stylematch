(function($){
    window.l=function(){l.history=l.history||[];l.history.push(arguments);if(this.console){console.log(Array.prototype.slice.call(arguments))}};

    // Need to be here, else Internet Explorer crap, will cache all ajax requests -> sad end-winblows-user
    $.ajaxSetup({
        cache: false
    });

    window.Event = Backbone.Model.extend({ });
    window.EventCollection = Backbone.Collection.extend({
        model:Event,
        // Set by the django template
        url: CALENDAREVENTS_API_URL,
    });


    window.BlockTableItemView = Backbone.View.extend({
        tagName:"td",
	busy: false,
	blockViewsIndex: 0,
        //template:_.template($('#tpl-inspiration-image-list-item').html()),
        initialize:function() {
            _.bindAll(this, 'mouseover');
        },
        render:function (eventName) {
            $(this.el).html();
            return this;
        },
        events:{
	    'mouseover': 'mouseover',
	    'mouseleave': 'mouseleave',
        },
	setBusy: function() {
	    this.busy = true;
	    $(this.el).addClass("busy");
	},
	removeBusy: function() {
	    this.busy = false;
	    $(this.el).removeClass("busy");
	},
	highlight: function() {
	    $(this.el).addClass("highlight");
	},
	unHighlight: function() {
	    $(this.el).removeClass("highlight");
	},
	reset: function() {
	    this.removeBusy();
	    this.unHighlight();
	},
	mouseover: function() {
	    this.options.parent.trigger('possibleToBook', this.blockViewsIndex, this.options.blockViewsRow);
	    this.$el.addClass('block-hover');
	},
	mouseleave: function () {
	    this.$el.removeClass('block-hover');
	    this.options.parent.trigger('unHighlightBlocks');
	},
        close:function () {
            $(this.el).unbind();
            $(this.el).remove();
        }
    });

    window.EventView = Backbone.View.extend({
        el: $("body"),
	currentTopDate: DATE_TODAY, //the date that is displayed in the first row, starts at the todays date
	cutNumberOfBlocks: 4, //this is the number of time-blocks the choosed cut/cuts take
	weekDay: {0: "mån", 1: "tis", 2: "ons", 3: "tors", 4: "fre", 5: "lör", 6: "sön"},
        initialize:function () {
            //Glue code, that initialize's all views and models
            this.eventList = new EventCollection();
	    this.on('possibleToBook', this.possibleToBook, this);
	    this.on('unHighlightBlocks', this.unHighlightBlocks, this);
	    _.bindAll(this, 'success', 'selectService');

	    this.fetch();
	    this.createBlocks();
	    //_.bindAll(this, 'loadData', 'fetchSuccess'); 
	    
        },
	events: {
	    'click #but': 'fetchNextWeek',
	    'click #but2': 'fetchPreviousWeek',
	    'click .service-book-me': 'selectService',
	},
	fetch: function() {
	    var data = {_start_time: this.currentTopDate};
	    // end_time needs to be the date + 1, or django will filter the last date
	    var date_next_week = this.getDateDaysAhead(this.parseDate(this.currentTopDate), 7)
	    var date_formatted = this.formatDate(date_next_week);
	    data['_end_time'] = date_formatted;
		
	    this.eventList.fetch({
		data: data,
		success: this.success
	    });
	  
	},
	success: function(collection, response) {
	    console.log("a",collection);
            if(!response) {
                var noty_id = noty({
                    text: 'Frisörens schema kunde inte hämtas för tillfället-',
                    type: 'error'
                });
            }
	    this.fillBusyBlocks();
	    this.displayDates();
        },
	selectService: function(event) {
	    var service_id = $(event.currentTarget).attr('id');

	    // same service but in the clientbooking service list
	    var service_in_dropdown = $('#service-dropdown').find('#service-dropdown-id-' + service_id);
	    var service_length = service_in_dropdown.find('.service-dropdown-length').text();
	    console.log(service_length);
	    var length_in_blocks = service_length / 15;
	    this.cutNumberOfBlocks = length_in_blocks;

	    return false;
	},
	formatDate: function(date) {
	    //YYYY-MM-DD
	    return date.getFullYear() + "-" + this.padZeros(date.getMonth() + 1) + "-" + date.getDate();
	},
	fetchNextWeek: function() {
	    var date_next_week = this.getDateDaysAhead(this.parseDate(this.currentTopDate), 7);
	    this.currentTopDate = this.formatDate(date_next_week);
	    this.resetBlocks();
	    this.fetch();
	    return false;
	},
	fetchPreviousWeek: function() {
	    var date_next_week = this.getDateDaysAhead(this.parseDate(this.currentTopDate), -7);
	    this.currentTopDate = this.formatDate(date_next_week);
	    this.resetBlocks();
	    this.fetch();
	    return false;
	},
	possibleToBook: function(blockViewsIndex, blockViewsRow) {
	    /*
	     * Responsible for filling the nearest not busy blocks
	     * when hovering over a block.
	     */

	    // TODO: check exceptions - when at first or last block (or near)
	    
	    // the current select block need to be free, else we dont need to check more blocks
	    var view = blockViewsRow[blockViewsIndex];
	    if(view.busy == true) { return false }
	    
	    var sum_not_busy_blocks = 1;
	    this.not_busy_blocks = [];	    
	    this.not_busy_blocks.push(view);

	    for(i=1; i<this.cutNumberOfBlocks;) {
		//console.log('t',i,blockViewsIndex+parseInt(i));
		var view = blockViewsRow[blockViewsIndex+i]
		if(view == null || view.busy == true) {
		    //should only count consequent empty time-blocks
		    break;
		} else {
		    sum_not_busy_blocks = ++sum_not_busy_blocks;
		    this.not_busy_blocks.push(view);
		    //console.log("not busy");
		}
		i=++i;
	    }
	    
	    for(i=1; i<this.cutNumberOfBlocks;) {
		console.log('t',i,blockViewsIndex-i);
		// if true, we have enough consquent free time-blocks
		if(sum_not_busy_blocks == this.cutNumberOfBlocks) {
		    break;
		}
		var view = blockViewsRow[blockViewsIndex-i]
		if(view == null || view.busy == true) {
		    break;
		    console.log("busy");
		} else {
		    sum_not_busy_blocks = ++sum_not_busy_blocks;
		    this.not_busy_blocks.push(view);
		    console.log("not busy");
		}
		i=++i;
	    }
	    
	    if(sum_not_busy_blocks == this.cutNumberOfBlocks) {
		_.each(this.not_busy_blocks, function(block) {
		    block.highlight();
		});
	    }
	    
	},
	resetBlocks: function() {
	    _.each(_.flatten(this.blockViews), function(view) {
		view.reset();
	    });
	},
	unHighlightBlocks: function() {
	    _.each(this.not_busy_blocks, function(block) {
		block.unHighlight();
	    });
	},
	padZeros: function(number) {
	    length = 2;
	    var str = '' + number;
	    while (str.length < length) {
		str = '0' + str;
	    }
	    return str;
	},
	displayDates: function() {
	    var start_date = this.parseDate(this.currentTopDate); var date_formatted; var date;
	    var unordered_list = $('#dates').html("");
	    for(i = 0; i < 7; i++) {
		date_formatted = this.weekDay[start_date.getDay()] + " " + this.padZeros(start_date.getMonth() + 1) + "/" + start_date.getDate();
		unordered_list.append("<li>" + date_formatted + "</li>");
		start_date = this.getDateDaysAhead(start_date, 1)
	    }
	    
	    //console.log(readable_date);
	},
	getOpeningTime: function() {
	    // should be fetched from profile's openinghours 
	    return 8;
	},
	getClosingTime: function() {
	    // should be fetched from profile's openinghours 
	    // dont forget it may be a string
	    return 17;
	},
	createBlockRow: function(number_of_blocks) {
	    var block_views_row = []; var current_block;
	    var current_tr = $("<tr></tr>");
	    $('table').append(current_tr);
	    var right_block = false
	    while(number_of_blocks-- > 0) {
	 	//sum = ++sum;
		//console.log("hi", current_tr);
		var className;
		// this should be decided on the time level, i.e. if starttime is 8.15 this should be the right block
		if(right_block) {
		    className = "block right";
		    right_block = false;
		}
		else {
		    right_block = true;
		    className = "block left";
		}
		current_block = new BlockTableItemView({parent: this, blockViewsRow: block_views_row, className: className});
		current_tr.append(current_block.render().el);
		var i = block_views_row.push(current_block) - 1;
		current_block.blockViewsIndex = i;
	    }
	    return block_views_row;
	},
	createBlocks: function() {
	    /*
	     * Creates all blocks on a page
	     */

	    //TODO: this is okay if opening/closing time is a integer, i.e. 8, but not if it's 8.30
	    var number_of_openhours = this.getClosingTime() - this.getOpeningTime();
	    // four blocks for each hour
	    var number_of_blocks = number_of_openhours * 4;
	    
	    this.blockViews = [];
	    i = 7;
	    // display 7 days
	    while(i-- > 0) {
		this.blockViews.push(this.createBlockRow(number_of_blocks));
	    }

	},
	getDateDaysAhead: function(date_object, days_ahead) {
	    // get the date x days forward from date_object
	    if(days_ahead == null) { days_ahead = 0}
	    date_object.setTime(date_object.getTime() + days_ahead * 1000 * 3600 * 24);
	    return date_object;
	},
	getBlockRow: function(event_date) {
	    // returns block row that corresponds to the date
	    var day_in_milliseconds = 1000*3600*24;
	    var milliseconds_later = this.parseDate(event_date) - this.parseDate(this.currentTopDate);
	    var days_later = milliseconds_later / day_in_milliseconds;
	    return days_later;
	},
	numberOfBlocksToFill: function(start_time, end_time) {
	    // TODO: this function need to handle: 13.00, 13.15, 13.30, 13.45
	    // currently it only cares about the first part: 13, 14 etc
	    var start_time_parts =  start_time.split(":");
	    var end_time_parts =  end_time.split(":");
	    var number_of_blocks = (end_time_parts[0] - start_time_parts[0]) * 4;
	    return number_of_blocks;
	},
	parseDate: function(str) {
	    //YYYYmmdd or YYYY-mm-dd
	    
	    // remove all non digits
	    str = str.replace(/\D/g,'');
	    var y = str.substr(0,4),
            m = str.substr(4,2) - 1,
            d = str.substr(6,2);
	    var D = new Date(y,m,d);
	    return (D.getFullYear() == y && D.getMonth() == m && D.getDate() == d) ? D : 'invalid date';
	},
	setBlocksBusy: function(start_time, number_of_blocks, block_row) {    
	    /*
	     * Marks blocks as busy starting at block that corresponds to start_time and x number_of_blocks ahead
	     */

	    // should use this.numberOfBlocksToFill, when getOpeningTIme returns string
	    var opening_time = this.getOpeningTime();
	    start_time = start_time.split(":")[0];
	    var start_block = (start_time - opening_time) * 4;
	    var block_views_row = this.blockViews[block_row];
	    while(number_of_blocks > 0) {
		block_views_row[start_block + number_of_blocks].setBusy();
		number_of_blocks = --number_of_blocks;
	    }
	},
	fillBusyBlocks: function() {
	    /*
	     * Takes every calendarEvent for the current week
	     * and marks the corresponding timeblocks as busy
	     */

	    l(this.EventList);
	    var start_time; var end_time;
	    _.each( this.eventList.models, function (event) {
		console.log(event);
		start_time = event.get('start_time').split("T")[1]
		end_time = event.get('end_time').split("T")[1]

		number_of_blocks = this.numberOfBlocksToFill(start_time, end_time);

		var block_row = this.getBlockRow(event.get('start_time').split("T")[0]);
		l('fillbusyblocks', start_time, end_time, number_of_blocks, block_row);
		this.setBlocksBusy(start_time, number_of_blocks, block_row);

            }, this);
	},
	inactiveBlocks: function() {
	    /*
	     * Marks groups of blocks as inactive. If there's not enough following 'not busy blocks'
	     * for the currently select cut, they are marked as inactive and greyed out.
	     */
	    _.each(this.blockViews, function(blockRow) {
		_.each(blockRow, function(block) {
		    console.log(block);
		});
	    });
	},

        render:function (eventName) {
            return this;
        },
        close:function () {
            $(this.el).unbind();
            $(this.el).empty();
        }
    });
    this.EventView = new EventView();

})(jQuery);

