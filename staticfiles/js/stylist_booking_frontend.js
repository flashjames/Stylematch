$(function(){
    var Event = Backbone.Model.extend({
	parse: function(response) {
	    this.start = new Date(Date.parse(response.start_time));;
	    this.end = new Date(Date.parse(response.end_time));;
	    this.title = response.title;
	    this.id = response.id;
	    return response;
	},
    });

    var EventCollection = Backbone.Collection.extend({
        model: Event,
        url: CALENDAREVENTS_API_URL
    });

    var EventsView = Backbone.View.extend({
        el: $("#calendar"),
        initialize: function(){
            _.bindAll(this);

            //this.collection.bind('reset', this.addAll);
            //this.collection.bind('add', this.addOne);
            //this.collection.bind('change', this.change);
            //this.collection.bind('destroy', this.destroy);
            this.eventList = new EventCollection();

            this.$calendar = $(this.el).weekCalendar({
                timeslotsPerHour: 4,
                timeslotHeigh: 30,
                hourLine: true,
                data: this.data,
		timeFormat: "h:i",
		firstDayOfWeek: 1,
		use24Hour: true,
		timeSeparator: " - ",
		buttonText: {today : "idag", lastWeek : "<", nextWeek : ">"},
		shortMonths:  ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'],
		shortDays: ['Sön', 'Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör'],
		useShortDayNames: true,
		businessHours: {start: 8, end: 18, limitDisplay: true}, //TODO: these times should be set with openhours
                height: function($calendar) {
                    return $(window).height(); //- $('h1').outerHeight(true);
                },
                eventNew: this.createEvent,
		changedate: this.fetch,
                //eventMouseover: this.test,
            });
            this.fetch();
	    _.bindAll(this,'createEvent');

        },
	data: function(start, end, callback) {
	    callback(this.eventList.models);
	},
        fetch: function() {
	    var end_date = this.$calendar.weekCalendar('getCurrentLastDay');

	    // Need to have end_date one day ahead, since django filtering skips the last day
	    end_date = new Date(end_date.setTime(end_date.getTime() + 1000 * 3600 * 24));

            var data_filtering = {_start_time: this.formatDate(this.$calendar.weekCalendar('getCurrentFirstDay')),
                        _end_time: this.formatDate(end_date)};

	    var _this = this;
            this.eventList.fetch({
                data: data_filtering,
                success: function(collection, response) {
		    _this.$calendar.weekCalendar("refresh");
                }
            });

        },
        test: function() {
            console.log("triggered");
        },
	createEvent: function(calEvent, element, dayFreeBusyManager, 
                                                    calendar, mouseupEvent) {
	    console.log(calEvent, element, dayFreeBusyManager, calendar, mouseupEvent, this.eventList, this.jsDateToDjango(calEvent.start), this.jsDateToDjango(calEvent.end), calEvent.title);
	    this.eventList.create({start_time: this.jsDateToDjango(calEvent.start), 
				   end_time: this.jsDateToDjango(calEvent.end), 
								 title: calEvent.title});
	    //calEvent.title
	},
	jsDateToDjango: function(date_object) {
	    // formats javascript date to django date
	    // YYYY-MM-DD T HH:MM
	    var django_formatted = date_object.getFullYear() + "-" + this.padZeros(date_object.getMonth() + 1) + "-" + this.padZeros(date_object.getDate()) + "T" + this.padZeros(date_object.getHours()) + ":" + this.padZeros(date_object.getMinutes());
	    return django_formatted;
	},

        /* COMMON FUNCTIONS WITH CLIENT BOOKING */

        padZeros: function(number) {
            length = 2;
            var str = '' + number;
            while (str.length < length) {
                str = '0' + str;
            }
            return str;
        },
        formatDate: function(date) {
            //YYYY-MM-DD
            return date.getFullYear() + "-" + this.padZeros(date.getMonth() + 1) + "-" + date.getDate();
        },


    });

    var EventView = Backbone.View.extend({
        el: $('#eventDialog'),
        initialize: function() {
            _.bindAll(this);
        },
        render: function() {
        },
    });


    this.EventView = new EventsView();
    //events.fetch();
});
