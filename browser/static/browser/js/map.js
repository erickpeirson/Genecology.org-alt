function geographic_visualization(network_id) {
	$('div[id="network-visualization"]').empty();
	

	// Timeseries chart.
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
											//[53.5, -4.5]
	var map = new L.Map("network-visualization", {center: [40,-100], zoom: 4})
		.addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

	var svg = d3.select(map.getPanes().overlayPane).append("svg"),
		  g = svg.append("g").attr("class", "leaflet-zoom-hide");

	function getBounds(nodes) {
		var left = 0, 
			bottom = 90,
			right = 0,
			top = 0;
		nodes.forEach( function(node) {
			if (node.geographic.latitude > top) {
				top = node.geographic.latitude;
			}
			if (node.geographic.latitude < bottom) {
				bottom = node.geographic.latitude;
			}	
			if (node.geographic.longitude < left) {
				left = node.geographic.longitude;
			}						
			if (node.geographic.longitude > right) {
				right = node.geographic.longitude;
			}									
		});
		console.log([[left, bottom],[right,top]]);
		return [[left-10, bottom-10],[right+10,top+10]];
	}
	
	// Used to assign colors to nodes, based on their type.
	var color = d3.scale.category10();
	var types = [];
	var t_index = 0;



	// Arrays for indexing various things.
	var hash_lookup = [];	// Node id -> Node element.
	var edge_hash_lookup = [];  // Edge id -> Edge element.
	var concept_lookup = {};
	var relations_predicates = {};  // Predicate -> Relation.
	var predicates_relations = {};  // Relation -> Predicate.
	var relations_lookup = {};	// Relations -> Edge.
	var edges_lookup = {}; // Edge -> Relations.
	var nodes_lookup = {}; // Node -> Appellations.
	var appellations_lookup = {}; // Appellations -> Node.
	
	
	//"/networks/network/"+network_id+"/"
	d3.json("/networks/network/"+network_id+"/projection/1/", function(graph) {
		// Index nodes by id, and index types (for color-coding).
		graph.network.nodes.forEach(function(d, i) {
			hash_lookup[d.id] = d;
			concept_lookup[d.concept] = d;
			if (!types[d.type]) {
				types[d.type] = t_index*3;
				t_index++;		
			}
		
			nodes_lookup[d.id] = Array();
			d.appellations.forEach(function(b, j) {
				nodes_lookup[d.id].push(b);
				appellations_lookup[b] = d;
			});
		});
		
		// Find source and target objects for each edge, and index edge by relation.
		graph.network.edges.forEach(function(d, i) {
			d.source = hash_lookup[d.source];
			d.target = hash_lookup[d.target];

			edges_lookup[d.id] = Array();
			d.relations.forEach(function(b, j) {
				relations_lookup[b] = d;
				edges_lookup[d.id].push(b);
				edge_hash_lookup[d.id] = d;
			});
		});

		var transform = d3.geo.transform({point: projectPoint}),
			path = d3.geo.path().projection(transform),
			bounds = getBounds(graph.network.nodes);
	
		var edge = g.selectAll(".edge")
					.data(graph.network.edges)
					.enter()
					.append("svg:line")
					.classed('edge', true)
					.classed("leaflet-zoom-hide", true)
					.attr("id", function(d) {
						return d.id;
					})					 
					.on("click", function(d) {	// User clicks an edge in the network.
						// Identify the appellations of relations for this edge.
						var rel_targets = Array();
						edges_lookup[d.id].forEach( function(i) {
							var id = predicates_relations[i];
							var e_app = d3.select('a.appellation[id="' + id + '"]')[0][0]
							rel_targets.push(e_app);
						});
						activate_edge(d, rel_targets);		
					});

		var node = g.selectAll(".node")
						.data(graph.network.nodes)
						.enter()
						.append("svg:circle");
		
		node.classed("leaflet-zoom-hide", true)
            .classed("node", true)
            .attr("id", function (d) { return d.id; })		
            .style("fill", function(d) { 	// Color nodes based on their type.
                return color(types[d.type]);
            })
				
		node.on("click", function (d) {		// User clicks a node in the network.
			var app_targets = Array();
			nodes_lookup[d.id].forEach( function(i) {
				var n_app = d3.select('a.appellation[id="' + i + '"]')[0][0]
				app_targets.push(n_app);
			});
			activate_node(d, app_targets);
		});

		// Add labels to nodes.
		var label = g.selectAll(".label")
		            .data(graph.network.nodes)
		            .enter()
                    .append("svg:text")
                    .classed("label", true)
//                     .attr("dx", function(d) { return -d.label.length*3 } )
//                     .attr("dy", -12)
                    .text(function(d) { return d.label; });

		label.on("click", function (d) {		// User clicks a node in the network.
			var app_targets = Array();
			nodes_lookup[d.id].forEach( function(i) {
				var n_app = d3.select('a.appellation[id="' + i + '"]')[0][0]
				app_targets.push(n_app);
			});
			activate_node(d, app_targets);
		});

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

			node.attr("cx", function(d) { 
					var c = d.geographic;
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[0]; 
				})
				.attr("cy", function(d) { 
					var c = d.geographic;
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[1]; 
				})
				.attr("r", function(d) { return 10; });

			edge.attr("x1", function(d) {
					var c = d.geographic.source; 
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[0];
				})
				.attr("y1", function(d) {   
					var c = d.geographic.source; 
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[1];
				})
				.attr("x2", function(d) {   
					var c = d.geographic.target; 
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[0];
				})
				.attr("y2", function(d) {   
					var c = d.geographic.target; 
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[1];
				});
				
			label.attr("x", function(d) {
					var c = d.geographic;
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[0] - d.label.length*3;// + Math.random()*20; 
				})
				.attr("y", function(d) { 
					var c = d.geographic;
					var ll = projectPoint(c.longitude,c.latitude);
					return ll[1] + (Math.random()-0.5)*30; 
				});
		}

		function projectPoint(x, y) {
			var point = map.latLngToLayerPoint(new L.LatLng(y, x));
			return Array(point.x, point.y);
		}
	
		var chart = timeseries_chart().x(get_time)
										.y(get_magnitude).yLabel("Size")
										.brushmove(on_brush);

		check_active();

		function check_active() {
			// An 'active' node or edge may have been passed from another page. If so, activate it.
			var active_node = $.urlParam('active_node');
			if (active_node) {
				var this_node = hash_lookup[active_node];
				var these_appellations = [];
				this_node.appellations.forEach(function(a) {
					these_appellations.push( d3.select('a.appellation[id="'+a+'"]')[0][0] );
				});
				activate_node(this_node, these_appellations);
			}
	
			var active_edge = $.urlParam('active_edge');
			if (active_edge) {
				console.log(active_edge);
				var this_edge = edge_hash_lookup[active_edge];
				var these_relations = this_edge.relations;
				var these_appellations = [];
				these_relations.forEach( function(r) {
					these_appellations.push( d3.select('a.appellations[id="'+predicates_relations[r]+'"]')[0][0] );
				});
				activate_edge(this_edge, these_appellations);
		
			}	
		}

		// Clears all 'focal' classes from nodes, edges, appellations.
		function deselect_all() {
			// De-select all
			d3.select(".node.focal")
				.classed("focal", false)
				.attr("r", 10);	
			
			edge.classed("focal", false);
			d3.select('a.appellation.focal').classed("focal", false)	
			
		}

		// Highlights node, and corresponding appellations.
		//	intext is a list of appellation elements in the text.	
		function activate_node(d, intext) {
			d.fixed = 1;
			deselect_all();

			// Select the focal node
			d.focal = true;
			console.log(d);
			d3.select(".node[id=\"" + d.id + "\"]")
				.classed("focal", true)
				.attr("r", 15);
		
			if (text_present) {
			    var moved = false;
				intext.forEach( function(i) {
					if (i) {    // Not all appellations are found in this text.
						d3.select('a[id="' + i.id + '"]').classed("focal", true);
						if (!moved) {   // Reposition page to first appellation.
						    moved = true;
                            $('#'+i.id).goTo();						    
						}
					}
				});
				console.log(intext);

			}
				
			show_node_details(d);
		}
	
		// Highlights edge, and corresponding appellations.
		//	intext is a list of appellation elements in the text.
		function activate_edge(d, intext) {
			deselect_all();
			console.log(d.id);
			d3.select('line[id="' + d.id + '"]')
				.classed("focal", true);

			d.focal = true;
		
			if (text_present) {
				intext.forEach( function(i) {
					if (i) {
						d3.select('a[id="' + i.id + '"]').classed("focal", true);
					}
				});
			}
		
			show_edge_details(d);
		}
	
		function show_node_texts(d) {
			$.get("/networks/node/appellations/"+d.id+"/", function(data) {
				console.log(data);
				var texts = {};
				data.appellations.forEach( function(a) {
				    if (a.textposition) {
    					if (! texts[a.textposition.text] ){
	    					texts[a.textposition.text] = a.textposition;
		    			}
		    		}
				});
		
				var values = Object.keys(texts).map(function(key){
					return texts[key];
				});
	
				$('.element_texts_title').text(d.label + ' appears in...');
				var element_texts = d3.select('.element_texts_list');
				$('.element_texts_list').empty();
				var text = element_texts
							.selectAll('li')
							.data(values)
							.enter()
							.append('li')
							.append('a')
							.attr('href', function(r) {
								return "/browser/texts/"+r.text_id+"/?active_node="+d.id;
							})
							.text( function(r) { 
								return r.text_title;
							} );
			});
		}
	
		function show_edge_texts(d) {
			$.get("/networks/edge/relations/"+d.id+"/", function(data) {
					
				var texts = {};
				data.relations.forEach( function(a) {
					if (! texts[a.predicate.text] ){
						texts[a.predicate.text] = a.predicate;
					}
				});
			
				var values = Object.keys(texts).map(function(key){
					return texts[key];
				});
		
				$('.element_texts_title').text('Relationship appears in...');
				var element_texts = d3.select('.element_texts_list');
				$('.element_texts_list').empty();
				var text = element_texts
							.selectAll('li')
							.data(values)
							.enter()
							.append('li')
							.append('a')
							.attr('href', function(r) {
								return "/browser/texts/"+r.text_id+"/?active_edge="+d.id;
							})
							.text( function(r) { 
								return r.text_title;
							} );
			});
		}
	
		function show_node_details(d) {
			$('div[id="instructions"]').empty();
			d3.select('.element_details_title').text(d.label);
			d3.select('.element_details_uri').text(d.concept);
			d3.select('.element_details_type').text(d.type);
			show_node_texts(d);
		
			$('[id="network-link"]').empty();
			$('[id="network-link"]').append('<a href="/browser/networks/?active_node='+d.id+'">See node in context</a>');
		}
	
		function show_edge_details(d) {
			$('div[id="instructions"]').empty();
			d3.select('.element_details_title').text(d.source.label + ' [' + d.label + '] ' + d.target.label);
			d3.select('.element_details_uri').text(d.concept);
			show_edge_texts(d);
		
			$('[id="network-link"]').empty();
			$('[id="network-link"]').append('<a href="/browser/networks/?active_edge='+d.id+'">See edge in context</a>');        
		}
		//d3.select('div[id="time-select"]').datum(graph.nodes).call(chart);
	});

}