(function($){
    var login_url = "http://sffbokning.extenda.se/boka/CJStudioUnique/login.aspx";
    var login_name = "n0rdics@hotmail.com";
    var login_password = "dinmamma";

    var input_uname = $('#ctl02_teUserName');
    var input_password = $('#ctl02_tePassword');

    var viewstate = '__VIEWSTATE';
    var viewstate_val;
    var eventvalidation = '__EVENTVALIDATION';
    var eventvalidation_val;

    function login() {
        $.get('http://sffbokning.extenda.se/boka/cjstudiounique/login.aspx', function(response, status, xhr) {
	    console.log("got login page");
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
        var viewstate_reg = /(__VIEWSTATE\|)(\/[A-Za-z0-9\/\+]*)/;
        var result = employee_page.match(viewstate_reg);
        viewstate_val = result[2];
        eventvalid_reg = /(__EVENTVALIDATION\|)(\/[A-Za-z0-9\/\+]*)/;
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
            console.log(success);
        });

    }

    $(document).ready(function() {
	login();
    });


})(jQuery);
