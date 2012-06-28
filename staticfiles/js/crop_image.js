$(window).load(function(){
    function updateCoords(c)
    {
	// updates the form input fields, which will be sent to Django
	jQuery('#id_start_x_coordinate').val(Math.round(c.x));
	jQuery('#id_start_y_coordinate').val(Math.round(c.y));
	jQuery('#id_width').val(Math.round(c.w));
	jQuery('#id_height').val(Math.round(c.h));
    };
    
    var jcrop_api;
    if(IMAGE_REAL_WIDTH < 220 || IMAGE_REAL_HEIGHT < 220) {
	jcrop_api = $.Jcrop('#jcrop_target');
	$('#warning-small-picture').show();
    } else {

	jcrop_api = $.Jcrop('#jcrop_target', {
	    trueSize: [IMAGE_REAL_WIDTH, IMAGE_REAL_HEIGHT], // trueSize: http://deepliquid.com/content/Jcrop_Sizing_Issues.html
	    minSize: [220,220] // dont let selection box become smaller than specified values
	});
    }
    
    // keep aspectRatio on the selection box and update form input fields
    jcrop_api.setOptions({ aspectRatio: 1/1, onSelect: updateCoords});
    jcrop_api.focus();
    var bounds = jcrop_api.getBounds();
    var bound_width = bounds[0];
    var bound_height = bounds[1];
    var padding_x_coordinate = 0; var padding_y_coordinate = 0; var square_side_length = 0;
    // is width or height the limiting bound, which should be used
    // to specify size of (width and height) of the box?
    if(bound_height < bound_width) {
	square_side_length = bound_height;
	// used to center the selection box
	padding_x_coordinate = (bound_width-bound_height)/2;
    } else {
	square_side_length = bound_width;
	// used to center the selection box
	padding_y_coordinate = (bound_height-bound_width)/2;
    }
    
    /*
    Selection rectangle on the image
    Rectangle - First two values is upper left, the other two are lower right
    [Start x-coordinate, Start y-coordinate, End x-coordinate, End y-coordinate]
     */
    jcrop_api.setSelect([0+padding_x_coordinate,0+padding_y_coordinate,square_side_length+padding_x_coordinate,square_side_length+padding_y_coordinate]);
	
});