// this function makes it easier to switch to change data source and data format
// all functions that take values from the data object use this function
function get_value(data_point) {
    return parseInt(data_point.visits);
}

var data = visitor_count_data;
var margin = {top: 10, right: 42, bottom: 20, left: 42},
width = 420 - margin.left - margin.right,
height = 200 - margin.top - margin.bottom;

var y = d3.scale.linear().domain([0, d3.max(data, function(d) { return get_value(d); })]).range([height, 0]),
x = d3.scale.linear().domain([0, data.length]).range([0, width])

var line = d3.svg.line()
//.interpolate("monotone")
    .x(function(d, i) { return x(i); })
    .y(function(d, i) { return y(get_value(d)); });

// the svg we write on
var svg = d3.select("#profile-visitor-statistics").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .attr("class","svg-charts")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


// does this do anything useful? I see it in all examples, but cant
// find any difference visually.
svg.append("defs").append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("width", width)
    .attr("height", height);

// does this do anything useful? I see it in all examples, but cant
// find any difference visually.
var path = svg.append("g")
    .attr("clip-path", "url(#clip)")
    .append("path")
    .data([data])
    .attr("class", "line")
    .attr("d", line);

// area generator
var area = d3.svg.area()
//.interpolate("monotone")
    .x(function(d, i) { return x(i); })
    .y0(height)
    .y1(function(d) { return y(get_value(d)); });

// Add the area path.
svg.append("g")
    .append("svg:path")
    .attr("class", "area")
    .attr("clip-path", "url(#clip)")
    .attr("d", area(data));

// points on the line, where each data-point is
// also adds mouseover/mouseout bindings
svg.selectAll(".point")
    .data(data)
    .enter()
    .append("circle")
    .attr("r", 4)
    .attr("cx", function(d, i) {
        return x(i);
    })
    .attr("cy", function(d) {
        return y(get_value(d))
    })
    .on("mouseover", tooltip_on)
    .on("mouseout", tooltip_off);

// tooltip on mouseover data-point
function tooltip_on(d) {
    var chart_tooltip = _.template($('#chart-tooltip').html(), {'visitor_count': d.visits, 'start_date': d.start_date, 'end_date': d.end_date});
    $("body").append(chart_tooltip);

    var position = $(d3.select(this)[0]).offset();
    $("#tooltip").offset({ top: position.top-16, left: position.left+20});

    d3.select(this)
        .attr("stroke", "orange")
        .attr("stroke-width", 5)
        .attr("stroke-opacity", 0.6);
}

// remove the tooltip on mouseout
function tooltip_off() {
    $('#tooltip').remove();
    d3.select(this)
        .attr("stroke", "none");
}

// x-axis
svg.append("svg:line")
    .attr("x1", x(0))
    .attr("y1", y(0))
    .attr("x2", width)
    .attr("y2", y(0))

// This axis is only used to place start-date and end-date on the right place
// the axis is hidden with css
var xAxis = d3.svg.axis()
    .tickFormat(function(d,i,k) {
	// display end_date on x-axis
	if(d > 0) {
	    return data[d].end_date
	}
	// display start date on x-axis
	return data[d].start_date;
    })
    .scale(x)
    .tickValues([0,data.length-1])
    .orient("bottom");

// Add the x-axis.
svg.append("svg:g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

// y-axis
svg.append("svg:line")
    .attr("x1", x(0))
    .attr("y1", y(0))
    .attr("x2", x(0))
    .attr("y2", y(d3.max(data, function(d) { return get_value(d); })))

