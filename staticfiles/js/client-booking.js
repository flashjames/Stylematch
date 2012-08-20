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
	inactive: false,
	blockViewsIndex: 0,
	highlighted: false,
	closed: false,
        initialize:function() {
            _.bindAll(this, 'mouseover', 'book');
        },
        render:function (eventName) {
            $(this.el).html();
            return this;
        },
        events:{
	    'mouseover': 'mouseover',
	    'mouseleave': 'mouseleave',
	    'click': 'book',
        },
	findStartBlock: function() {
	    /*
	     * Finds the start block index, of the group of blocks, which represents the event, client want to book
	     */
	    var i = this.blockViewsIndex;
	    while(true) {
		i = --i;
		console.log("here",i);
		
		// we may already be at the first block, then return that index. because then it's our start block
		if(i < 0) {console.log("crap");return 0};
		
		//if the tested block was not highlighted, we now the block before was our start block
		if(!this.options.blockViewsRow[i].highlighted) return i+1;
	    }
	},
	blocksToMinutes: {0: "00", 1: "15", 2: "30", 3: "45"},
	getTimesForEvent: function() {
	    /*
	     * Returns the start_time and end_time the selected blocks represent
	     */
	    var opening_time_hour = parseInt(EARLIEST_OPENING.split(":")[0], 10),
	    start_block_index = this.findStartBlock();

	    // start time
	    var block_hours_start = Math.floor(start_block_index / 4);
	    var hours_start = opening_time_hour + block_hours_start;
	    var minutes_start = start_block_index % 4;
	    var minutes_formatted_start = this.blocksToMinutes[minutes_start];

	    // end_time
	    var block_hours_end = Math.floor((start_block_index + this.options.parent.cutNumberOfBlocks) / 4);
	    var hours_end = opening_time_hour + block_hours_end;
	    var minutes_end = (start_block_index + this.options.parent.cutNumberOfBlocks) % 4;
	    var minutes_formatted_end = this.blocksToMinutes[minutes_end];

	    return [hours_start + ":" + minutes_formatted_start, hours_end + ":" + minutes_formatted_end]
	},
	getDate: function() {
	    var parent = this.options.parent;
	    var start_date = parent.parseDate(parent.currentTopDate);
	    date = parent.getDateDaysAhead(start_date, this.options.blockViewsRowIndex)
	    date_formatted = date.getFullYear() + "-" + parent.padZeros(date.getMonth() + 1) + "-" + date.getDate();
	    console.log(date_formatted, this.options.blockViewsRowIndex);
	    return date_formatted;
	},
	book: function() {
	    var parent = this.options.parent;
	    if(this.inactive || this.busy) return false

	    // get start- and end-time for the calendarevent the client want to book
	    var time = this.getTimesForEvent(),
	    start_time = time[0],
	    end_time = time[1],
	    date = this.getDate(),
	    django_formatted_starttime = date + "T" + start_time,
	    django_formatted_endtime = date + "T" + end_time;
	    
	    if(!parent.selectedServices) {
		l("no service selected");
	    }

	    //TODO: handle booking of multiple services
	    var service_id = parent.selectedServices[0];
	    console.log(django_formatted_starttime, django_formatted_endtime);
	    parent.eventList.create({start_time: django_formatted_starttime, 
				     end_time: django_formatted_endtime, 
				     title: 'booked_online'});
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
	    this.highlighted = true;
	    $(this.el).addClass("highlight");
	},
	unHighlight: function() {
	    this.highlighted = false;
	    $(this.el).removeClass("highlight");
	},
	setInactive: function() {
	    this.inactive = true;
	    $(this.el).addClass("inactive");
	},
	removeInactive: function() {
	    this.inactive = false;
	    if(!this.closed) {
		$(this.el).removeClass("inactive");
	    }
	},
	setClosed: function() {
	    this.closed = true;
	    $(this.el).addClass("inactive");
	},
	removeClosed: function() {
	    this.closed = false;
	    if(!this.inactive) {
		$(this.el).removeClass("inactive");
	    }
	    $(this.el).removeClass("inactive");
	},

	reset: function() {
	    this.removeBusy();
	    this.unHighlight();
	    this.removeInactive();
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
	currentTopDate: DATE_TODAY, //the date that is displayed in the first row, starts at the todays date  TODO: remove the wrong default
	cutNumberOfBlocks: 8, //this is the number of time-blocks the choosed cut/cuts take
	weekDay: {0: "sön", 1: "mån", 2: "tis", 3: "ons", 4: "tors", 5: "fre", 6: "lör"}, // start of week is sunday, in Date()
	selectedServices: [1], //TODO: Remove this default
	blocksPerRow: null, // number of blocks each row is
        initialize:function () {
            //Glue code, that initialize's all views and models
            this.eventList = new EventCollection();
	    this.on('possibleToBook', this.possibleToBook, this);
	    this.on('unHighlightBlocks', this.unHighlightBlocks, this);
	    _.bindAll(this, 'success', 'selectService');
	    
	    this.blocksPerRow = this.getBlocksPerRow();
	    this.fetch();
	    this.createBlocks();
	    this.displayTimes();
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
            if(!response) {
                var noty_id = noty({
                    text: 'Frisörens schema kunde inte hämtas för tillfället-',
                    type: 'error'
                });
            }
	    this.fillBusyBlocks();
	    this.displayDates();

	    this.blocksOutsideOpenhours();
	    this.setInactiveBlocks();
        },
	selectService: function(event) {
	    var service_id = $(event.currentTarget).attr('id');

	    // same service but in the clientbooking service list
	    var service_in_dropdown = $('#service-dropdown').find('#service-dropdown-id-' + service_id);
	    this.selectedServices = [service_id];
	    var service_length = service_in_dropdown.find('.service-dropdown-length').text();
	    var length_in_blocks = service_length / 15;
	    this.cutNumberOfBlocks = length_in_blocks;
	    this.setInactiveBlocks();
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
	    if(view.busy == true || view.closed == true) { return false }
	    
	    var sum_not_busy_blocks = 1;
	    this.not_busy_blocks = [];	    
	    this.not_busy_blocks.push(view);

	    for(i=1; i<this.cutNumberOfBlocks;) {
		//console.log('t',i,blockViewsIndex+parseInt(i));
		var view = blockViewsRow[blockViewsIndex+i]
		if(view == null || view.busy == true || view.closed == true) {
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
		// if true, we have enough consquent free time-blocks
		if(sum_not_busy_blocks == this.cutNumberOfBlocks) {
		    break;
		}
		var view = blockViewsRow[blockViewsIndex-i]
		if(view == null || view.busy == true || this.closed == true) {
		    break;
		} else {
		    sum_not_busy_blocks = ++sum_not_busy_blocks;
		    this.not_busy_blocks.push(view);
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
		start_date = this.getDateDaysAhead(start_date, 1);
	    }
	    
	    //console.log(readable_date);
	},
	displayTimes: function() {
	    // TODO: fix so it can handle 8:15, 8:30..
	    var opening_time = parseInt(this.getOpeningTime().split(":")[0], 10);
	    var closing_time = parseInt(this.getClosingTime().split(":")[0], 10);
	    var hours = closing_time - opening_time;
	    for(var i = 0; i < hours;) {
		if(i == 0) {
		    var first_part = "<li class='first'>";
		} else {
		    var first_part = "<li>";
		}
		$('#times').append(first_part + (opening_time + i) +"</li>");
		i = ++i;

	    }
	},
	getOpeningTime: function() {
	    // should be fetched from profile's openinghours 
	    return EARLIEST_OPENING;
	},
	getClosingTime: function() {
	    // should be fetched from profile's openinghours 
	    // dont forget it may be a string
	    //return 17;
	    return LATEST_CLOSING;
	},
	createBlockRow: function(number_of_blocks, blockViewsRowIndex) {
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
		current_block = new BlockTableItemView({parent: this, blockViewsRow: block_views_row, className: className, blockViewsRowIndex: blockViewsRowIndex});
		current_tr.append(current_block.render().el);
		var i = block_views_row.push(current_block) - 1;
		current_block.blockViewsIndex = i;
	    }
	    return block_views_row;
	},
	getBlocksPerRow: function() {
	    /*
	     * Returns number of blocks between earliest OpeningTime and  latest ClosingTime
	     */
	    return this.numberOfBlocksBetween(this.getOpeningTime(), this.getClosingTime())
	},
	createBlocks: function() {
	    /*
	     * Creates all blocks on a page
	     */
	    this.blockViews = [];
	    i = 7;
	    // display 7 days
	    for(i = 0; i < 7;) {
		this.blockViews.push(this.createBlockRow(this.blocksPerRow, i));
		i = ++i;
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
	blocksForMinutes: {'15': 1, '30': 2, '45': 3, '00': 0},
	numberOfBlocksBetween: function(start_time, end_time) {
	    var start_time_parts =  start_time.split(":");
	    var end_time_parts =  end_time.split(":");
	    
	    // add blocks for minutes
	    
	    var blocks_minutes = this.blocksForMinutes[end_time_parts[1]] - this.blocksForMinutes[start_time_parts[1]];
	    var blocks_hours = (end_time_parts[0] - start_time_parts[0]) * 4;

	    return blocks_hours + blocks_minutes;
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

	    var start_block = this.numberOfBlocksBetween(this.getOpeningTime(), start_time);
	    console.log(start_block);
	    var block_views_row = this.blockViews[block_row];
	    for(i=0; i < number_of_blocks; ++i) {
		var index_in_array = start_block + i
		
		// an event can have an end/start time, that's outside openinghours.
		// this if-case makes sure we dont try to set blocks that should correspond to
		// these blocks (which do not exist)
		if(index_in_array >= this.blocksPerRow) return
                
		// we can also get value's that's lower than zero -> skip ahead to next index
		if(index_in_array < 0) continue;

		block_views_row[index_in_array].setBusy();
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

		number_of_blocks = this.numberOfBlocksBetween(start_time, end_time);

		var block_row = this.getBlockRow(event.get('start_time').split("T")[0]);
		l('fillbusyblocks', start_time, end_time, number_of_blocks, block_row);
		this.setBlocksBusy(start_time, number_of_blocks, block_row);

            }, this);
	},
	setBlocksInactive: function(blocks) {
	    _.each(blocks, function(block) {
		block.setInactive();
	    });
	},
	setInactiveBlocks: function() {
	    /*
	     * Marks groups of blocks as inactive. If there's not enough following 'not busy blocks'
	     * for the currently select cut, they are marked as inactive and greyed out.
	     */
	    _this = this;
	    _.each(this.blockViews, function(blockRow, outer_index) {
		var needed_empty_blocks = _this.cutNumberOfBlocks;
		current_blocks = [],

		_.each(blockRow, function(block, index) {
		    // since we may have selected a new Cut with shorter length
		    // we need to remove the inactive class for all blocks
		    block.removeInactive();

		    // we can have set, block as inactive before with blocksOutsideOpenhours
		    if(!block.busy && !block.closed) {
			needed_empty_blocks = --needed_empty_blocks;
			current_blocks.push(block);
		    } else {
			if(needed_empty_blocks > 0) {
			    _this.setBlocksInactive(current_blocks);
			}
			needed_empty_blocks = _this.cutNumberOfBlocks;
			current_blocks = []
		    }
		    if(outer_index == 5 && index > 10) {
			debugger;
		    }

		});

		// the last block on the row may not be a busy block
		// since the if-case above only set's inactive when a busy block is found
		// we need to check if enough 'not busy' blocks were found or not
		if(needed_empty_blocks > 0) {
		    _this.setBlocksInactive(current_blocks);
		}
	    });
	},
	blocksOutsideOpenhours: function() {
	    /* 
	     * Set blocks outside openhours as inactive.
	     * This is needed since we show blocks for all days according to earliest opening/closing
	     * and days can have different openhours + can be closed.
	     */
	    var date = this.parseDate(this.currentTopDate);

	    // total number of blocks on a row
	    for(i = 0; i < 7; i++) {
		var openhours = this.getOpenHours(date);
		if(openhours.success) {
		    var index_block_opening = this.numberOfBlocksBetween(EARLIEST_OPENING, openhours.open_times)
		    for(x=0; x < index_block_opening;x++) {
			this.blockViews[i][x].setClosed();
		    }
		    var index_block_closing = this.numberOfBlocksBetween(EARLIEST_OPENING, openhours.closed_times);
		    for(x=index_block_closing; x < this.blocksPerRow; x++) {
			this.blockViews[i][x].setClosed();
		    }
		} else {
		    // whole day closed
		    _.each(this.blockViews[i], function(block) {
			block.setClosed();
		    });
		}
		date = this.getDateDaysAhead(date, 1);
	    }
	},
	/* COMMON FUNCTIONS WITH STYLIST BOOKING */

	getOpenHours: function(date_object) {
	    /*
	     * Returns opening and closing hours for supplied date (the weekday for the date)
	     */

	    /* WARNING!! .split() IS REMOVED IN THIS FUNCTION. IF ILL REFACTOR OUT COMMON FUNCTIONS */

	    // in OPENING_HOURS, monday have index 0. but in Date.getDay() sunday have 0 -> convert it
	    var weekday_integer = (date_object.getDay() + 6) % 7
	    
	    // it's possible the day is closed
	    try {
		//debugger;
		var success = true;
		var open_times = OPENING_HOURS[weekday_integer].open;
		var closed_times = OPENING_HOURS[weekday_integer].closed;

		// test if it's closed
		OPENING_HOURS[weekday_integer].open.split(":");
	    } catch(TypeError) {
		var success = false;
	    }
	    return {success: success, open_times: open_times, closed_times: closed_times}
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

