var node_radius = 8;

var map = new L.Map("map", {center: [53.5, -4.5], zoom: 6})
    .addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

var svg = d3.select(map.getPanes().overlayPane).append("svg"),
    g = svg.append("g").attr("class", "leaflet-zoom-hide");

d3.json("/static/browser/data/features.json", function(collection) {
    var transform = d3.geo.transform({point: projectPoint}),
        path = d3.geo.path().projection(transform),
        bounds = d3.geo.bounds(collection);
      
	feature = g.selectAll("circle")
				 .data(collection.features)
				 .enter().append("svg:circle")
				 .classed("leaflet-zoom-hide", true)
				 .classed("mapnode", true);
	
	edge = g.selectAll("line")
	            .data(collection.edges)
	            .enter().append("svg:line")
				 .classed("leaflet-zoom-hide", true)
				 .classed("mapedge", true);
    map.on("viewreset", reset);
    reset();

    function reset() {
        var topLeft = projectPoint(bounds[0][0], bounds[1][1]),
            bottomRight = projectPoint(bounds[1][0], bounds[0][1]);

        svg.attr("width", bottomRight[0] - topLeft[0] + node_radius*2)
           .attr("height", bottomRight[1] - topLeft[1] + node_radius*2)
           .style("left", topLeft[0]-node_radius + "px")
           .style("top", topLeft[1]-node_radius + "px");

        g.attr("transform", "translate(" + -(topLeft[0]-node_radius) + "," + -(topLeft[1]-node_radius) + ")");

        feature.attr("cx", function(d) { 
                    var c = d.geometry.coordinates;
                    var ll = projectPoint(c[0],c[1]);
                    return ll[0]; 
                })
                .attr("cy", function(d) { 
                    var c = d.geometry.coordinates;
                    var ll = projectPoint(c[0],c[1]);
                    return ll[1]; 
                })
                .attr("r", function(d) { return d.properties.size*2; });
        
        edge.attr("x1", function(d) {
                var c = d.coordinates[0]; 
                var ll = projectPoint(c[0],c[1]);
                return ll[0];
            })
            .attr("y1", function(d) {   
                var c = d.coordinates[0]; 
                var ll = projectPoint(c[0],c[1]);
                return ll[1];
            })
            .attr("x2", function(d) {   
                var c = d.coordinates[1]; 
                var ll = projectPoint(c[0],c[1]);
                return ll[0];
            })
            .attr("y2", function(d) {   
                var c = d.coordinates[1]; 
                var ll = projectPoint(c[0],c[1]);
                return ll[1];
            })
            .style("stroke-width", function(d) { 
                return Math.sqrt(d.properties.strength); 
            });
    }

    function projectPoint(x, y) {
        var point = map.latLngToLayerPoint(new L.LatLng(y, x));
        return Array(point.x, point.y);
    }
    
    var chart = timeseries_chart()
                    .x(get_time)
                    .y(get_magnitude).yLabel("Size")
                    .brushmove(on_brush);
    d3.select("body").datum(collection.features).call(chart);
});

