$(function(){
    var Event = Backbone.Model.extend({
        parse: function(response) {
            // after a save on the model, parse is called with response==null
            if(response == null) return

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
                //eventNew: this.createEvent,
                changedate: this.fetch,
                eventDrop: this.changedEvent,
                eventResize: this.changedEvent,
                eventNew: this.createEvent,
                eventClick: this.editEvent,


            });
            this.fetch();
            //_.bindAll(this,'createEvent');

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
        editEvent: function(calEvent, $event) {

            if (calEvent.readOnly) {
                return;
            }

            var $dialogContent = $("#event_edit_container");
            //resetForm($dialogContent);
            var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
            var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
            var titleField = $dialogContent.find("input[name='title']").val(calEvent.title);
            var bodyField = $dialogContent.find("textarea[name='body']");
            bodyField.val(calEvent.body);
	    var _this = this;
            $dialogContent.dialog({
                modal: true,
                title: "Edit - " + calEvent.title,
                close: function() {
                    $dialogContent.dialog("destroy");
                    $dialogContent.hide();
                    $('#calendar').weekCalendar("removeUnsavedEvents");
                },
                buttons: {
                    save : function() {

                        calEvent.start = new Date(startField.val());
                        calEvent.end = new Date(endField.val());
                        calEvent.title = titleField.val();
                        calEvent.body = bodyField.val();

			_this.changedEvent(calEvent);
                        _this.$calendar.weekCalendar("updateEvent", calEvent);
                        $dialogContent.dialog("close");
                    },
                    "delete" : function() {
			var event_model = _this.getOriginalModel(calEvent);
			console.log(event_model);
			event_model.destroy();
                        _this.$calendar.weekCalendar("removeEvent", calEvent.id);

                        $dialogContent.dialog("close");
                    },
                    cancel : function() {
                        $dialogContent.dialog("close");
                    }
                }
            }).show();

            var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
            var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
            $dialogContent.find(".date_holder").text(this.$calendar.weekCalendar("formatDate", calEvent.start));
            this.setupStartAndEndTimeFields(startField, endField, calEvent, this.$calendar.weekCalendar("getTimeslotTimes", calEvent.start));
            $(window).resize().resize(); //fixes a bug in modal overlay size ??

        },
        createEvent: function(calEvent, $event) {
            var $dialogContent = $("#event_edit_container");
            //resetForm($dialogContent);
            var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
            var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
            var titleField = $dialogContent.find("input[name='title']");
            var bodyField = $dialogContent.find("textarea[name='body']");
	    var _this = this;
	    
            $dialogContent.dialog({
                modal: true,
                title: "New Calendar Event",
                close: function() {
                    $dialogContent.dialog("destroy");
                    $dialogContent.hide();
                    $('#calendar').weekCalendar("removeUnsavedEvents");
                },
                buttons: {
                    save : function() {
                        //calEvent.id = id;
                        //id++;
			calEvent.id = 100;
                        calEvent.start = new Date(startField.val());
                        calEvent.end = new Date(endField.val());
                        calEvent.title = titleField.val();
                        calEvent.body = bodyField.val();

			// we need to access this event in createEventSuccess, made it global. i'm a baaad man :<
			_this.calEventWaiting = calEvent;

              		
			// save event to database
			_this.eventList.create({start_time: _this.jsDateToDjango(calEvent.start),
					       end_time: _this.jsDateToDjango(calEvent.end),
					       title: calEvent.title}, { success: _this.createEventSuccess});

                        $dialogContent.dialog("close");
                    },
                    cancel : function() {
                        $dialogContent.dialog("close");
                    }
                }
            }).show();

            $dialogContent.find(".date_holder").text(this.$calendar.weekCalendar("formatDate", calEvent.start));
            this.setupStartAndEndTimeFields(startField, endField, calEvent, this.$calendar.weekCalendar("getTimeslotTimes", calEvent.start));
        },
	createEventSuccess: function(collection, model) {
	    //TODO: check for error and then use notify
	    this.calEventWaiting.id = model.id;
	    this.$calendar.weekCalendar("removeUnsavedEvents");
            this.$calendar.weekCalendar("updateEvent", this.calEventWaiting);
	},
        setupStartAndEndTimeFields: function($startTimeField, $endTimeField, calEvent, timeslotTimes) {
            /*
             * Sets up the start and end time fields in the calendar event
             * form for editing based on the calendar event being edited
             */
            var $endTimeField = $("select[name='end']");
            var $endTimeOptions = $endTimeField.find("option");
            var $timestampsOfOptions = {start:[],end:[]};

            //reduces the end time options to be only after the start time options.
            $("select[name='start']").change(function() {
                var startTime = $timestampsOfOptions.start[$(this).find(":selected").text()];
                var currentEndTime = $endTimeField.find("option:selected").val();
                $endTimeField.html(
                    $endTimeOptions.filter(function() {
                        return startTime < $timestampsOfOptions.end[$(this).text()];
                    })
                );

                var endTimeSelected = false;
                $endTimeField.find("option").each(function() {
                    if ($(this).val() === currentEndTime) {
                        $(this).attr("selected", "selected");
                        endTimeSelected = true;
                        return false;
                    }
                });

                if (!endTimeSelected) {
                    //automatically select an end date 2 slots away.
                    $endTimeField.find("option:eq(1)").attr("selected", "selected");
                }

            });


            $startTimeField.empty();
            $endTimeField.empty();

            for (var i = 0; i < timeslotTimes.length; i++) {
                var startTime = timeslotTimes[i].start;
                var endTime = timeslotTimes[i].end;
                var startSelected = "";
                if (startTime.getTime() === calEvent.start.getTime()) {
                    startSelected = "selected=\"selected\"";
                }
                var endSelected = "";
                if (endTime.getTime() === calEvent.end.getTime()) {
                    endSelected = "selected=\"selected\"";
                }
                $startTimeField.append("<option value=\"" + startTime + "\" " + startSelected + ">" + timeslotTimes[i].startFormatted + "</option>");
                $endTimeField.append("<option value=\"" + endTime + "\" " + endSelected + ">" + timeslotTimes[i].endFormatted + "</option>");

                $timestampsOfOptions.start[timeslotTimes[i].startFormatted] = startTime.getTime();
                $timestampsOfOptions.end[timeslotTimes[i].endFormatted] = endTime.getTime();

            }
            $endTimeOptions = $endTimeField.find("option");
            $startTimeField.trigger("change");
        },
	getOriginalModel: function(calEvent) {
	    /*
	     * Returns the backbone model corresponding to the calEvent (which is a copy of the origin model)
	     */
	    return this.eventList.get(calEvent.id);
	},
        changedEvent: function(calEvent) {
            var event_model = this.getOriginalModel(calEvent);
            event_model.attributes.start_time = this.jsDateToDjango(calEvent.start);
            event_model.attributes.end_time = this.jsDateToDjango(calEvent.end);
            event_model.attributes.title = calEvent.title;
            event_model.save({silent:true});
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

    this.EventView = new EventsView();
});
