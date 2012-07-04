var data = [3, 6, 2, 7, 5, 2, 1, 0, 8, 900, 2, 5, 1];

var margin = {top: 10, right: 10, bottom: 20, left: 10},
width = 420 - margin.left - margin.right,
height = 200 - margin.top - margin.bottom;


var y = d3.scale.linear().domain([0, d3.max(data)]).range([height, 0]),
x = d3.scale.linear().domain([0, data.length]).range([0, width])

//
var line = d3.svg.line()
//.interpolate("monotone")
    .x(function(d, i) { return x(i); })
    .y(function(d, i) { return y(d); });

// the svg we write on
var svg = d3.select("#bar-demo").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// does this do anything useful? I see it in all examples, but cant
// find any difference visually.
svg.append("defs").append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("width", width)
    .attr("height", height);

var path = svg.append("g")
    .attr("clip-path", "url(#clip)")
    .append("path")
    .data([data])
    .attr("class", "line")
    .attr("d", line);

var area = d3.svg.area()
//.interpolate("monotone")
    .x(function(d, i) { return x(i); })
    .y0(height)
    .y1(function(d) { return y(d); });

// Add the area path.
svg.append("g")
    .append("svg:path")
    .attr("class", "area")
    .attr("clip-path", "url(#clip)")
    .attr("d", area(data));

// points on the line, where each data-point is
svg.selectAll(".point")
    .data(data)
    .enter()
    .append("circle")
    .attr("r", 4)
    .attr("cx", function(d, i) {
        return x(i);
    })
    .attr("cy", function(d) {
        return y(d)
    })
    .on("mouseover", tooltip_on)
    .on("mouseout", tooltip_off);

// add tooltip on mouseover data-point
function tooltip_on() {
    var chart_tooltip = _.template($('#chart-tooltip').html(), {'visitor_count': 800, 'start_date': '2012-13-14', 'end_date': '2012-17-14'});
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

// y-axis
svg.append("svg:line")
    .attr("x1", x(0))
    .attr("y1", y(0))
    .attr("x2", x(0))
    .attr("y2", y(d3.max(data)))
