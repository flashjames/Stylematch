//var data = {{ data|safe }};
//console.log(asd);
var data = [3, 6, 2, 7, 5, 2, 1, 3, 8, 9, 2, 5, 1],
w = 820,
h = 200,
margin = 40,
y = d3.scale.linear().domain([0, d3.max(data)]).range([0 + margin, h - margin]),
x = d3.scale.linear().domain([0, data.length]).range([0 + margin, w - margin])

var vis = d3.select("#bar-demo")
    .append("svg:svg")
    .attr("width", w)
    .attr("height", h)

var g = vis.append("svg:g")
    .attr("transform", "translate(0, 200)");

var line = d3.svg.line()
    .x(function(d,i) { return x(i); })
    .y(function(d) { return -1 * y(d); })
    

var s = g.append("svg:path")
    .attr("d", line(data));


g.selectAll(".point")
    .data(data)
    .enter()
    .append("circle")
    .attr("r", 4)
    .attr("cx", function(d, i) {
        return x(i);
    })
    .attr("cy", function(d) {
	return -1 * y(d)
	console.log(y(d));
	return 50;
    })
    .on("mouseover", mouseover)
    .on("mouseout", mouseout);

function mouseover() {
    var chart_tooltip = _.template($('#chart-tooltip').html(), {'visitor_count': 800, 'start_date': '2012-13-14', 'end_date': '2012-17-14'});
    $("body").append(chart_tooltip);

    var position = $(d3.select(this)[0]).offset();
    $("#tooltip").offset({ top: position.top-16, left: position.left+20});

    d3.select(this)
	.attr("stroke", "orange")
	.attr("stroke-width", 5)
	.attr("stroke-opacity", 0.6);
}

function mouseout() {
    $('#tooltip').remove();
    d3.select(this)
	.attr("stroke", "none");
}


g.append("svg:line")
    .attr("x1", x(0))
    .attr("y1", -1 * y(0))
    .attr("x2", w - margin - 10)
    .attr("y2", -1 * y(0))

g.append("svg:line")
    .attr("x1", x(0))
    .attr("y1", -1 * y(0))
    .attr("x2", x(0))
    .attr("y2", -1 * y(d3.max(data)))


/*
ADD LABELS
g.selectAll(".xLabel")
    .data(x.ticks(3))
    .enter().append("svg:text")
    .attr("class", "xLabel")
    .text(String)
    .attr("x", function(d) { return x(d) })
    .attr("y", 0)
    .attr("text-anchor", "middle")

g.selectAll(".xTicks")
    .data(x.ticks(3))
    .enter().append("svg:line")
    .attr("class", "xTicks")
    .attr("x1", function(d) { return x(d); })
    .attr("y1", -1 * y(0))
    .attr("x2", function(d) { return x(d); })
    .attr("y2", -1 * y(-0.3))

*/
