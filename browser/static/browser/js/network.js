var map;

// For retrieve GET args.
$.urlParam = function(name){
	var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results==null) {
		return null;
	} else {
		return results[1] || 0;
	}
}

// Brings an element to the top of the display.
d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};

rangy.init();   // Rangy is used to work with text positions.

// These variables are used to assign colors to nodes, based on their type.
// TODO: Do this in a more consistent way.
var color = d3.scale.category10();
var types = [];
var t_index = 0;

// These arrays are for indexing various things.
// TODO: Figure out which of these can be done without.
var hash_lookup = [];	// Node id -> Node element.
var edge_hash_lookup = [];  // Edge id -> Edge element.
var concept_lookup = {};
var relations_predicates = {};  // Predicate -> Relation.
var predicates_relations = {};  // Relation -> Predicate.
var relations_lookup = {};	// Relations -> Edge.
var edges_lookup = {}; // Edge -> Relations.
var nodes_lookup = {}; // Node -> Appellations.
var appellations_lookup = {}; // Appellations -> Node.

// An 'active' node or edge may have been passed from another page; activate it.
var active_node = $.urlParam('active_node');
var active_edge = $.urlParam('active_edge');   

// Call this to pick up active edge or node in GET params.
function check_active() { 
    if (active_node) {
        var this_node = hash_lookup[active_node];
        var these_appellations = [];
        this_node.appellations.forEach( function(a) {
            var anc = d3.select('a.appellation[id="'+a+'"]')[0][0];
            these_appellations.push(anc);
        });
        activate_node(this_node, these_appellations);
    } else if (active_edge) {
        var this_edge = edge_hash_lookup[active_edge];
        var these_relations = this_edge.relations;
        var these_appellations = [];
        these_relations.forEach( function(r) {
            var anc = d3.select('a.appellations[id="'+predicates_relations[r]+'"]')[0][0]
            these_appellations.push(anchor);
        });
        activate_edge(this_edge, these_appellations);
    }	
}

// Call before activating/selecting nodes or edges.
function deselect_all() {
    d3.selectAll('.node.focal').attr("r", nodeSize);
    d3.selectAll('.focal').classed('focal', false);
}

// Highlights node, and corresponding appellations.
//	intext is a list of appellation elements in the text.	
function activate_node(d, intext) {
    deselect_all();

    // Select the focal node, and bring it to the front.
    d3.select('.label[id="' + d.id + '"]').classed("focal", true);    
    d3.select('.node[id="' + d.id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);
    d3.select('g[id="' + d.id + '"]').moveToFront();
    
    // Activate in-text appellations.
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
    }
    show_node_details(d);
    active_node = d.id;
}

// Highlights edge, and corresponding appellations.
//	intext is a list of appellation elements in the text.
function activate_edge(d, intext) {
    deselect_all();
    
    d3.select('line[id="' + d.id + '"]').classed("focal", true);

    d3.select('.label[id="' + d.target.id + '"]').classed("focal", true);
    d3.select('.label[id="' + d.source.id + '"]').classed("focal", true);
                    
    d3.select('.node[id="' + d.source.id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);
    d3.select('.node[id="' + d.target.id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);

    // Bring selected nodes to the top.
    d3.select('g[id="' + d.source.id + '"]').moveToFront();
    d3.select('g[id="' + d.target.id + '"]').moveToFront();

    d.focal = true;

    // Activate in-text appellations.
    if (text_present) {
        intext.forEach( function(i) {
            if (i) {    // Not all appellations are in this text.
                d3.select('a[id="' + i.id + '"]').classed("focal", true);
            }
        });
    }
    show_edge_details(d);
    active_edge = d.id;
}

// Displays the texts in which a particular node appears.
//  TODO: Make this easier to read; paging?
function show_node_texts(d) {
    $.get("/networks/node/appellations/"+d.id+"/", function(data) {
        // index textpositions for retrieval.
        var texts = {};
        data.appellations.forEach( function(a) {
            if (a.textposition) {
                if (! texts[a.textposition.text] ) {
                    texts[a.textposition.text] = a.textposition;
                }
            }
        });
        var values = Object.keys(texts).map(function(key){
            return texts[key];
        });

        // Generate the list.
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
                    .text( function(r) { return r.text_title; } );
    });
}

// Displays the texts in which a particular edge appears.
//  TODO: Make this easier to read; paging?
//  TODO: Combine with show_node_texts? (make this DRYer)
function show_edge_texts(d) {
    $.get("/networks/edge/relations/"+d.id+"/", function(data) {
        // index textpositions for retrieval.    
        var texts = {};
        data.relations.forEach( function(a) {
            if (! texts[a.predicate.text] ){
                texts[a.predicate.text] = a.predicate;
            }
        });
        var values = Object.keys(texts).map(function(key) {
            return texts[key];
        });

        // Generate the list.
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
                    .text( function(r) { return r.text_title; } );
    });
}

// Writes information about a node to .element_details content area.
function show_node_details(d) {
    $('div[id="instructions"]').empty();
    d3.select('.element_details_title').text(d.label);
    d3.select('.element_details_uri').text(d.concept);
    d3.select('.element_details_type').text(d.type);

	$('.element_contains_list').empty();
	if ('contains' in d) {
		d.contains.forEach( function (i) {
			d3.select('.element_contains_list').append('li').text(i.label);
		});
	}

    show_node_texts(d);

    $('[id="network-link"]').empty();
    var cm = '<a href="/browser/networks/?active_node='+d.id+'">See node in context</a>';
    $('[id="network-link"]').append(cm);
}

// Writes information about an edge to .element_details content area.
function show_edge_details(d) {
    $('div[id="instructions"]').empty();
    var title_text = d.source.label + ' [' + d.label + '] ' + d.target.label;
    d3.select('.element_details_title').text(title_text);
    d3.select('.element_details_uri').text(d.concept);
    
	$('.element_contains_list').empty();    
	if ('contains' in d) {
		d.contains.forEach( function (i) {
			var t = hash_lookup[i.source].label + ' [' + i.label + '] ' + hash_lookup[i.target].label;
			d3.select('.element_contains_list').append('li').text(t);
		});
	}    
    
    show_edge_texts(d);

    $('[id="network-link"]').empty();
    var cm = '<a href="/browser/networks/?active_edge='+d.id+'">See edge in context</a>';
    $('[id="network-link"]').append(cm);
}

// Indexes nodes and edges for quicker retrieval down the road.
// TODO: Simplify this, if possible.
function index_data(graph) {
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
}

// Called when user hovers over a node.
var mouseenter = function(e) {
    d = e.target;
    d3.select('.node[id="'+d.id+'"]').attr('r', nodeSize*2)
                                     .classed("hovered", true);        
    d3.select('.label[id="'+d.id+'"]').classed("hovered", true);
}

// Called when user hovers over an edge.
var mouseexit = function(e) {
    d = e.target;
    var hovered_node = d3.select('.node[id="'+d.id+'"]');
    hovered_node.attr('r', function(d) {
                            if (hovered_node.classed('focal')) {
                                return nodeSize*2;
                            } else {
                                return nodeSize;
                            }
                        })
                 .classed("hovered", false);        
    d3.select('.label[id="'+d.id+'"]').classed("hovered", false);            
}

// Adds an anchor element around each appellation's text-position.
var add_appellation = function(node, item) {
    try {
        var range = rangy.createRange();
        range.setStart(node.firstChild, item.textposition.startposition);
        range.setEnd(node.firstChild, item.textposition.endposition);

        var highlightNode = document.createElement('a');
        highlightNode.className = 'appellation';
        highlightNode.id = item.id;
        highlightNode.name = item.id;
        highlightNode.style.color = color(types[item.type]);
        range.surroundContents(highlightNode);
    } catch (err) {
        // Ignore appellations that overlap with those already added to the 
        //  text (handles cases wehre Rangy gets confused).
        // TODO: Something smarter than this.
    }
}

// Given some appellation data, marks-up the text with anchors, and binds as appropriate.
function process_appellations(data) {
    // Weed out appellations without text positions.
    var mappable = Array();
    data.appellations.forEach(function(item) {
        if ('textposition' in item) mappable.push(item)
    });

    // Sort appellations so that we can start adding them from the end of the text.
    mappable.sort(function (a,b) {
        if (a.textposition.startposition < b.textposition.startposition) return 1;
        if (a.textposition.startposition > b.textposition.startposition) return -1;
    });

    // Add appellations to the text.
    mappable.forEach(function(item) {
        add_appellation(textcontent, item);
    });

    // Index relations and their predicates.
    data.relations.forEach(function(item) {
        relations_predicates[item.predicate.id] = item.id;
        predicates_relations[item.id] = item.predicate.id;
    });

    // Bind apellation click event to activate the corresponding node or edge in the
    // 	network visualization.
    $('a.appellation').click(function(e) {
        if (relations_predicates[e.target.id]) {
            var this_edge = relations_lookup[relations_predicates[e.target.id]]
            activate_edge(this_edge, Array(e.target));
        } else {
            activate_node(appellations_lookup[e.target.id], [e.target]);
        }
    });
}

var edge_click = function(d) {	// User clicks an edge in the network.
    // Identify the appellations of relations that correspond to this edge.
    rel_targets = Array();
    edges_lookup[d.id].forEach( function(i) {
        var id = predicates_relations[i];
        rel_targets.push(d3.select('a.appellation[id="' + id + '"]')[0][0]);
    });
    activate_edge(d, rel_targets);		
}

var node_click = function (d) {		  // User clicks a node in the network.
    app_targets = Array();
    nodes_lookup[d.id].forEach( function(i) {
        app_targets.push(d3.select('a.appellation[id="' + i + '"]')[0][0]);
    });
    activate_node(d, app_targets);
}

var nodeSize;

function wrap(text, width) {
    text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 10, // ems
            dx = 0,
            dy = parseFloat(text.attr('dy')),
            tspan = text.text(null).append("tspan").attr("dy", dy).attr("dx", dx);            
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("dy", (++lineNumber * lineHeight) + dy)
                    .attr("dx", dx).text(word);
            }
        }
    });
}

function network_visualization(network_id) {
	d3.select('.element_contains').classed('hidden', true);

    try {
        map.remove();
    } catch (err) {
        // do nothing;    
    }
    $('div[id="network-visualization"]').empty()
	    .removeAttr('class')
	    .removeAttr('style')
	    .removeAttr('tabindex');

    var force_charge = -40;
    if (text_present) {
        var force_linkDistance = 40;
        nodeSize = 5;
        force_charge = -80;        
	} else {
        var force_linkDistance = 40;
        nodeSize = 5;
    }

	// Force-directed layout.
	var force = d3.layout.force()
		.charge(force_charge)
		.linkDistance(force_linkDistance)
		.size([width, height]);	

	// Initialize the network visualization SVG.
	var svg = d3.select("#network-visualization")
		.append("svg")
		.attr("width", width)
		.attr("height", height)
		.attr("pointer-events", "all")
		.append('svg:g')
		.call(d3.behavior.zoom()    // Zoomable.
		    .scaleExtent([1, 3.5])  // For some reason going below 1 gives weird behavior.
	    	.on("zoom", redraw))
		.append('svg:g');

	svg.append('svg:rect')          // Dragged during panning.
		.attr('width', width)
		.attr('height', height)
		.attr('fill', 'white');

	// Used to reposition the network when zooming/panning.
	function redraw() {
		svg.attr("transform", "translate(" + d3.event.translate + ")"
								 + " scale(" + d3.event.scale + ")");
	}			

	if (text_present) {
		var data_path = "/networks/network/text/"+text_id+"/";
	} else {
		var data_path = "/networks/network/"+network_id+"/";
	}

	// Almost all of the action happens once network data is loaded.
	d3.json(data_path, function(error, graph) {
        index_data(graph);

        // Updates node and edge positions.
        function tick() {
            edge.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });

            node.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        }

		// Initialize layout.
// 		force.nodes(graph.network.nodes)
//             .links(graph.network.edges)
//             .on("tick", tick)
//             .start();        // Update node and edge positions based on force-directed layout.
        
        // Dragging behavior.
        var node_drag = d3.behavior.drag();
//                .on("dragstart", dragstart)
//                .on("drag", dragmove)
//                .on("dragend", dragend);        

        function dragstart(d, i) {
            force.stop();
        }

        function dragmove(d, i) {
            d.px += d3.event.dx;
            d.py += d3.event.dy;
            d.x += d3.event.dx;
            d.y += d3.event.dy; 
            //tick();
        }

        function dragend(d, i) {
            d.fixed = true;
            //tick();
            force.resume();
        }	            

        // Draw edges.
        var edge = svg.selectAll(".edge")
            .data(graph.network.edges)
            .enter()
            .append("svg:line")
            .classed('edge', true)
            .attr("id", function(d) {
                return d.id;
            })
            .on("click", edge_click);

		// Draw nodes.
		var node = svg.selectAll(".node")
			.data(graph.network.nodes)
			.enter().append("g")
			.attr('id', function(d) {   return d.id; })
			.call(node_drag);   // Custom force.drag behavior.

		node.append("svg:circle")
            .classed("node", true)
			.attr("id", function (d) { return d.id; })		
			.attr("r", nodeSize)              // -vv- Color nodes based on their type.
			.style("fill", function(d) { return color(types[d.type]); });

        d3.json("/networks/layout/2/", function(error, layout) {
			node.attr("cx", function(d) {
				return layout[d.id].x*width;
			}).attr("cy", function(d) {
				return layout[d.id].y*height;
			});
			
			edge.attr("x1", function(d) { return layout[d.source.id].x*width; })
                .attr("y1", function(d) { return layout[d.source.id].y*height; })
                .attr("x2", function(d) { return layout[d.target.id].x*width; })
                .attr("y2", function(d) { return layout[d.target.id].y*height; });
			
            node.attr("transform", function(d) {
            	var x = layout[d.id].x*width;
            	var y = layout[d.id].y*height;
                return "translate(" + x + "," + y + ")";
            });
        });

		node.on("click", node_click);

		// Add labels to nodes.
		node.append("text")
		    .classed("label", true)
			.attr("dx", function(d) { return -d.label.length*2 } )
			.attr("dy", -6)
			.attr("id", function(d) { return d.id })
			.text(function(d) { return d.label; })
			.call(wrap, 100);

        $('.node').hover(mouseenter, mouseexit);

        // If a text is present on this page, retrieve appellations and add in-text links.
		if (text_present) {
			// The /networks/appellations/ endpoint provides data for a specific text.
			$.get("/networks/appellations/"+text_id+"/", function(data) {
                process_appellations(data);
			});
		}
		
		check_active(); // Highlight active node or edge in GET params.
	});
}

function geographic_visualization(network_id) {
	d3.select('.element_contains').classed('hidden', false);

    try {
        map.remove();
    } catch (err) {
        // do nothing;    
    }

	$('div[id="network-visualization"]').empty(); 

    if (text_present) {
        nodeSize = 20;
    } else {
        nodeSize = 10;
    }
    
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
		return [[left-10, bottom-10],[right+10,top+10]];
	}
	
	d3.select('div[id="network-visualization"]').style('width', width+"px")
												.style('height', height+"px");
												
    map = new L.Map("network-visualization", {center: [40,-100], zoom: 4})
        .addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

    var svg = d3.select(map.getPanes().overlayPane).append("svg"),
      g = svg.append("g").attr("class", "leaflet-zoom-hide");
		  
    d3.json("/networks/network/"+network_id+"/projection/1/", function(graph) {										    
        index_data(graph);
        
		var transform = d3.geo.transform({point: projectPoint}),
			path = d3.geo.path().projection(transform),
			bounds = getBounds(graph.network.nodes);
			
		var edge = g.selectAll(".edge")
                .data(graph.network.edges)
                .enter()
                .append("svg:line")
                    .classed('edge', true)
                    .classed("leaflet-zoom-hide", true)
                    .attr("id", function(d) { return d.id; })					 
                    .on("click", edge_click);
                    
		var node = g.selectAll(".node")
                .data(graph.network.nodes)
                .enter()
                .append("svg:circle")
                .attr("r", nodeSize);

		node.classed("leaflet-zoom-hide", true)
            .classed("node", true)
            .attr("id", function (d) { return d.id; })		
            .style("fill", function(d) { 	// Color nodes based on their type.
                return color(types[d.type]);
            })
            .on("click", node_click);

        $('.node').hover(mouseenter, mouseexit);
                    
		// Add labels to nodes.
		var label = g.selectAll(".label")
		            .data(graph.network.nodes)
		            .enter()
                    .append("text")
                    .classed("label", true)
                    .text(function(d) { return d.label; })
                    .attr("id", function(d) { return d.id; })
                    .on("click", node_click);                 

		map.on("viewreset", reset);
		reset();
		                                         
		function reset() {
			var topLeft = projectPoint(bounds[0][0], bounds[1][1]),
				bottomRight = projectPoint(bounds[1][0], bounds[0][1]);

			svg.attr("width", bottomRight[0] - topLeft[0] + nodeSize*2)
			   .attr("height", bottomRight[1] - topLeft[1] + nodeSize*2)
			   .style("left", topLeft[0]-nodeSize + "px")
			   .style("top", topLeft[1]-nodeSize + "px");

			g.attr("transform", "translate(" + -(topLeft[0]-nodeSize) + "," + -(topLeft[1]-nodeSize) + ")");

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
				.attr("r", function(d) { return nodeSize; });

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
				
            if (map._zoom < 4) {
                d3.selectAll('.label').classed('hidden', true);
            } else {
                d3.selectAll('.label').classed('hidden', false);            
            }
		}

		function projectPoint(x, y) {
			var point = map.latLngToLayerPoint(new L.LatLng(y, x));
			return Array(point.x, point.y);
		}		
        check_active();
    });
}
