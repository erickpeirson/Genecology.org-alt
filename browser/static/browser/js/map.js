function geographic_visualization(network_id) {
	d3.select('div[id="network-visualization"]').empty(); // Clear it.
	/// Timeseries chart.
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
			ts_width = width - margin.left - margin.right,
			ts_height = 80;

		var x = d3.time.scale(),
			y = d3.scale.linear(),
			brush = d3.svg.brush().x(x).on("brush", _brushmove);

		function timeseries(selection) {
			selection.each(function (d) {
				x.range([0, ts_width]);
				y.range([ts_height, 0]);

				var series = d3.select(this).append("svg").attr("id", "timeseries")
						.attr("width", ts_width + margin.left + margin.right)
						.attr("height", ts_height + margin.top + margin.bottom)
						.append("g").attr("id", "date-brush")
						.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

				var x_axis = series.append("g")
						.attr("class", "x axis")
						.attr("transform", "translate(0," + ts_height + ")");

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
					.attr("width", ts_width - 1)
					.attr("height", ts_height - .25)
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

	/// The real stuff.
	var node_radius = 8;

	d3.select('div[id="network-visualization"]').style('width', width+"px")
												.style('height', height+"px");
											
	var map = new L.Map("network-visualization", {center: [53.5, -4.5], zoom: 6})
		.addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

	var svg = d3.select(map.getPanes().overlayPane).append("svg"),
		g = svg.append("g").attr("class", "leaflet-zoom-hide");

	d3.json("/networks/network/"+network_id+"/", function(collection) {
		console.log('got data');
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

		d3.select('div[id="time-select"]').datum(collection.features).call(chart);
	});

}