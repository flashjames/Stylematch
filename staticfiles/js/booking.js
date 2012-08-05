(function($){
    var input_uname = $('#ctl02_teUserName');
    var input_password = $('#ctl02_tePassword');

    var viewstate = '__VIEWSTATE';
    var viewstate_reg = /(__VIEWSTATE\|)(\/[A-Za-z0-9\/\+\=]*)/;
    var eventvalidation = '__EVENTVALIDATION';
    var eventvalid_reg = /(__EVENTVALIDATION\|)(\/[A-Za-z0-9\/\+\=]*)/;
    var current_date_val = '';

    function login() {
        $.get('http://sffbokning.extenda.se/boka/cjstudiounique/login.aspx', function(response, status, xhr) {
	    console.log("got login page");

	    var login_name = "n0rdics@hotmail.com";
	    var login_password = "dinmamma";

            var eventvalidation_val = $(response).find('#__EVENTVALIDATION').val();
            var viewstate_val = $(response).find('#__VIEWSTATE').val();
            //console.log(eventvalidation_val, viewstate_val);

            $.post('http://sffbokning.extenda.se/boka/cjstudiounique/login.aspx', {
                'ctl02$teUserName':login_name,
                'ctl02$tePassword':login_password,
                '__VIEWSTATE':viewstate_val,
                '__EVENTVALIDATION':eventvalidation_val,
                '__Asyncpost':'true',
                'ctl02$btnLogin':'Logga in',
                'scriptmanager':'ctl02$upLogin|ctl02$btnLogin',
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':''
            }, function(success) {
		console.log("logged in");
		follow_login_redirect();
            });


        });

    }
    function follow_login_redirect() {
        $.get('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx', function(success, status, xhr) {
            console.log("followed login redirect");
	    get_employees(success);
        });

    }
    function get_employees(follow_redirect_page) {
        var eventvalidation_val = $(follow_redirect_page).find('#__EVENTVALIDATION').val();
        var viewstate_val = $(follow_redirect_page).find('#__VIEWSTATE').val();

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
            'ctl04$teEmployeeDetailsDivPos':'',
            'ctl04$teHelpTextDivPos':'',
            'smScriptmanager':'ctl04$upMultiView|ctl04$lnkBookingChoiceEmployee',
            '__EVENTTARGET':'ctl04$lnkBookingChoiceEmployee',
            '__EVENTARGUMENT':''
        }, function(success) {
            console.log("got employees");
	    get_services(success);
        });

    }
    function get_services(employee_page) {
        var result = employee_page.match(viewstate_reg);
        viewstate_val = result[2];
        result = employee_page.match(eventvalid_reg);
        eventvalidation_val = result[2];
        //console.log('get_services - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
            'ctl04$bNextPage':'Nästa sida >>',
            'smScriptManager':'ctl04$upNavButtons|ctl04$bNextPage',
            'ctl04$ddlEmployeeCompetenceLevel':'0',
            'ctl04$cblEmployees$0':'on',
            'ctl04$teEmployeeDetailsDivPos':'',
            'ctl04$teHelpTextDivPos':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
            '__EVENTARGUMENT':''
        }, function(success) {
            console.log("got services");
            select_service(success);
        });

    }
    function select_service(service_page) {
	var result = service_page.match(viewstate_reg);
        viewstate_val = result[2];
        result = service_page.match(eventvalid_reg);
        eventvalidation_val = result[2];
        //console.log('get_services - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upServices|ctl04$gvServices',
	    'ctl04$teEmployeeDetailsDivPos':'',
	    'ctl04$gvServices$ctl02$CheckBoxButton':'on',
	    'ctl04$teHelpTextDivPos':'',
	    '__EVENTTARGET':'ctl04$gvServices',
	    '__EVENTARGUMENT':'Select$0', // select first service in list
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
        }, function(success) {
            console.log("selected service");
	    get_choose_date_page(success);
        });

    }
    function get_choose_date_page(selected_services) {
	var result = selected_services.match(viewstate_reg);
        viewstate_val = result[2];
        result = selected_services.match(eventvalid_reg);
        eventvalidation_val = result[2];
        //console.log('get_services - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upNavButtons|ctl04$bNextPage',
	    'ctl04$gvServices$ctl02$CheckBoxButton':'on',
	    'ctl04$teEmployeeDetailsDivPos':'',
	    'ctl04$teHelpTextDivPos':'',
	    '__EVENTTARGET':'',
	    '__EVENTARGUMENT':'',
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
	    'ctl04$bNextPage':'Nästa sida >>'
        }, function(success) {
            console.log("got date page");
            open_calendar(success);
        });

	
    }

    /*
      --DONE--
      Need to get the calendar, and get first value for __EVENTARGUMENT.
      This number is a int that is increased for every day
      Eg. okt 1 - 4500, okt 2, 4501 and so on.
      
      --TODO--
      For the next requests (for next dates), this should be increased automatically, 
      so we dont need to do a extra XHR request for every single date, to get this number.
     */

    function open_calendar(date_page) {
	var result = date_page.match(viewstate_reg);
        viewstate_val = result[2];
        result = date_page.match(eventvalid_reg);
        eventvalidation_val = result[2];
	current_date_reg = /\<input.*name="ctl04\$teBookingDateChoiceText".*value\=\"([0-9-]+)\"/;
	var date_result = date_page.match(current_date_reg);
	current_date_val = date_result[1];
        //console.log('open calendar - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upMultiView|ctl04$bBookingDateChoicePicker',
	    'ctl04%24teBookingDateChoiceText': current_date_val, //current-date - get from date_page request
	    'ctl04%24rblBookingDateChoiceOptions':'1',
	    'ctl04%24teEmployeeDetailsDivPos':'',
	    'ctl04%24teHelpTextDivPos':'',
	    '__EVENTTARGET':'',
	    '__EVENTARGUMENT':'',
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
	    'ctl04$bBookingDateChoicePicker.x':'22',
	    'ctl04$bBookingDateChoicePicker.y':'19'
        }, function(success) {
            console.log("open_calendar");
            get_next_month(success);
        });
    }
    
    function get_next_month(open_calendar) {
	var result = open_calendar.match(viewstate_reg);
        viewstate_val = result[2];
        result = open_calendar.match(eventvalid_reg);
        eventvalidation_val = result[2];

	var event_arg_reg = /<a href=\s?\s?\"\s?javascript\s?\:\s?\_\_doPostBack\(\'ctl04\$clBookingDateChoice\'\s?,\'(V[0-9]{2,4})\s?\'/g;
 
	// we have two matches with the regex, previous and next month
	// therefor we use exec() to get the second one.
	while( res = event_arg_reg.exec(open_calendar) ) {
	    event_arg = res[1];
	}

        //console.log('get next month - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upMultiView|ctl04$clBookingDateChoice',
	    'ctl04%24teBookingDateChoiceText': current_date_val, //current-date
	    'ctl04%24rblBookingDateChoiceOptions':'1',
	    'ctl04%24teEmployeeDetailsDivPos':'',
	    'ctl04%24teHelpTextDivPos':'',
	    '__EVENTTARGET':'ctl04$clBookingDateChoice',
	    '__EVENTARGUMENT': event_arg, // this could be a future problem, when does it reset? should have a logger return information on problems here.
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
        }, function(success) {
            console.log("get_next_month");
            select_date(success);
        });
    }


    function select_date(date_page) {
	var result = date_page.match(viewstate_reg);
        viewstate_val = result[2];
        result = date_page.match(eventvalid_reg);
        eventvalidation_val = result[2];
        //console.log('get_services - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upMultiView|ctl04$clBookingDateChoice',
	    'ctl04$teBookingDateChoiceText':'2012-10-18', // dynamic
	    'ctl04$chkBookingDateNextAvailableTime':'on',
	    'ctl04$rblBookingDateChoiceOptions':'1',
	    'ctl04$teEmployeeDetailsDivPos':'',
	    'ctl04$teHelpTextDivPos':'',
	    '__EVENTTARGET':'ctl04$clBookingDateChoice',
	    '__EVENTARGUMENT':'4626', // dynamic
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
        }, function(success) {
            console.log("selected date");
            get_timeslots_for_date(success);
        });

	
    }
    
    function get_timeslots_for_date(selected_date) {
	/* There can be more pages with times for a date, need to implement
	   functionality to get those */
	
	var result = selected_date.match(viewstate_reg);
        viewstate_val = result[2];
        result = selected_date.match(eventvalid_reg);
        eventvalidation_val = result[2];
        //console.log('get_services - viewstate and eventvalidation', eventvalidation_val, viewstate_val);

        $.post('http://sffbokning.extenda.se/boka/cjstudiounique/services.aspx?sname=cjstudiounique', {
	    'smScriptManager':'ctl04$upNavButtons|ctl04$bNextPage',
	    'ctl04$teBookingDateChoiceText':'2012-09-31',
	    'ctl04$rblBookingDateChoiceOptions':'1',
	    'ctl04$teEmployeeDetailsDivPos':'',
	    'ctl04$teHelpTextDivPos':'',
	    '__EVENTTARGET':'',
	    '__EVENTARGUMENT':'',
	    '__LASTFOCUS':'',
            '__VIEWSTATE':viewstate_val,
            '__EVENTVALIDATION':eventvalidation_val,
            '__ASYNCPOST':'true',
	    'ctl04$bNextPage':'Nästa sida >>'
        }, function(success) {
            console.log("get timeslots for date");
            console.log(success);
        });

	
    }


    $(document).ready(function() {
	console.log("start");
	login();
	console.log("end");
    });


})(jQuery);
