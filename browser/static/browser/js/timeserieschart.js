function get_time(d) {
    var dt = new Date();
    dt.setYear(d.properties.date);
    return dt;
}

function get_magnitude(d) {
    return d.properties.size;
}

function on_brush(brush) {
    var s = brush.extent();
    d3.selectAll(".mapnode").classed("selected", function (d) {
        var time = get_time(d);
        return s[0] <= time && time <= s[1];
    });
    d3.selectAll(".mapedge").classed("selected", function (d) {
        var time = get_time(d);
        return s[0] <= time && time <= s[1];    
    });
}

function timeseries_chart() {
    var color="green";
    
    var margin = { top: 5, right: 5, bottom: 40, left: 45 },
        width = 600 - margin.left - margin.right,
        height = 80;

    var x = d3.time.scale(),
        y = d3.scale.linear(),
        brush = d3.svg.brush().x(x).on("brush", _brushmove);

    function timeseries(selection) {
        selection.each(function (d) {
            x.range([0, width]);
            y.range([height, 0]);

            var series = d3.select(this).append("svg").attr("id", "timeseries")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g").attr("id", "date-brush")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var x_axis = series.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")");

            var y_axis = series.append("g")
                    .attr("class", "y axis");

           /* y_axis.append("text")
                .attr("class", "label")
                .attr("transform", "rotate(-90)")
                .attr("y", -40)
                .attr("dy", ".4em")
                .style("text-anchor", "end")
                .text(y_label); */
                
            series.append("clipPath")
                .attr("id", "clip")
                .append("rect")
                .attr("width", width - 1)
                .attr("height", height - .25)
                .attr("transform", "translate(1,0)");                
                
            series.append("g")
                    .attr("class", "brush")
                    .call(brush)
                    .selectAll("rect")
                    .attr("height", height)
                    .style("stroke-width", 1)
                    .style("stroke", "gray")
                    .style("fill", "black")
                    .attr("opacity", 0.3);

            x.domain(d3.extent(d, get_x));
            x_axis.call(d3.svg.axis().scale(x).orient("bottom"));

            y.domain(d3.extent(d, get_y));
            y_axis.call(d3.svg.axis().scale(y).orient("left"));

            series.append("g").attr("class", "timeseries")
                .attr("clip-path", "url(#clip)")
                .selectAll("circle")
                .data(d).enter()
                .append("circle")
                .style("stroke", color)
                .style("stroke-width", .8)
                .style("fill", color)
                .attr("opacity", .8)
                .attr("r", 2)
                .attr("transform", function (d) {
                    return "translate(" + x(get_x(d)) + "," + y(get_y(d)) + ")";
                });
        });
    }
    
    get_x = function(d) {
        var dt = new Date();
        dt.setYear(d.properties.date);
        return dt;
    }
    get_y = function(d) {
        return d.properties.size;
    }
    
    timeseries.x = function (accessor) {
        if (!arguments.length) return get_x;
        get_x = accessor;
        return timeseries;
    };

    timeseries.y = function (accessor) {
        if (!arguments.length) return get_y;
        get_y = accessor;
        return timeseries;
    };

    timeseries.xLabel = function (label) {
        if (!arguments.length) return x_label;
        x_label = label;
        return timeseries;
    }

    timeseries.yLabel = function (label) {
        if (!arguments.length) return y_label;
        y_label = label;
        return timeseries;
    }

    timeseries.brushmove = function (cb) {
        if (!arguments.length) return brushmove;
        brushmove = cb;
        return timeseries;
    };

    function _brushmove() {
        brushmove.call(null, brush);
    }

    return timeseries;
}