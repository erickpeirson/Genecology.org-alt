$.urlParam = function(name){
    var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}

// Rangy is used to work with text positions.
rangy.init();

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

// Force-directed layout.
var force = d3.layout.force()
    .charge(-400)
    .linkDistance(100)
    .size([width, height]);

// Initialize the network visualization SVG.
var svg = d3.select("#network-visualization")
	.append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("pointer-events", "all")
	.append('svg:g')
    .call(d3.behavior.zoom()
    .scaleExtent([0.2, 3.5])
    .on("zoom", redraw))
	.append('svg:g');

svg.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

// Used to refresh the network when zooming/panning.
function redraw() {
	svg.attr("transform", "translate(" + d3.event.translate + ")"
							 + " scale(" + d3.event.scale + ")");
}			

if (text_present) {
    var data_path = "/networks/network/text/"+text_id+"/"
} else {
    var data_path = "/networks/network/"+network_id+"/"
}

// Almost all of the action happens once network data is loaded.
d3.json(data_path, function(error, graph) {
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

	// Layout the graph.
	force
		.nodes(graph.network.nodes)
		.links(graph.network.edges)
		.start();

	// Draw edges.
	var link = svg.selectAll(".link")
		.data(graph.network.edges)
		.enter()
		.append("line")
		.attr("class", "link")
		.attr("id", function(d) {
			return d.id;
		})
		.on("click", function(d) {	// User clicks an edge in the network.
			// Identify the appellations of relations that correspond to this edge.
			rel_targets = Array();
			edges_lookup[d.id].forEach( function(i) {
				var id = predicates_relations[i];
				rel_targets.push(d3.select('a.appellation[id="' + id + '"]')[0][0]);
			});
			
			activate_edge(d, rel_targets);		
		 });

	// Draw nodes.
	var node = svg.selectAll(".node")
		.data(graph.network.nodes)
		.enter().append("g")
		.call(force.drag);

	node.append("circle")
		.attr("class", "node")
		.attr("id", function (d) { return d.id; })		
		.attr("r", 10)
		.style("fill", function(d) { 	// Color nodes based on their type.
			return color(types[d.type]);
		});

	node.on("click", function (d) {		// User clicks a node in the network.
		app_targets = Array();
		nodes_lookup[d.id].forEach( function(i) {
			app_targets.push(d3.select('a.appellation[id="' + i + '"]')[0][0]);
		});
		
		activate_node(d, app_targets);
	});

	// Add labels to nodes.
	node.append("text")
		.attr("dx", function(d) { return -d.label.length*3 } )
		.attr("dy", -12)
		.text(function(d) { return d.label; });

  // Update node and edge positions based on force-directed layout.
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
        
    node.attr("transform", function(d) {
    	return "translate(" + d.x + "," + d.y + ")";
    });
  });
  
  // Stops force-directed layout.
 /* var stop = d3.select("#stop-layout").on("click", function () { 
		if (d3.select("#stop-layout").attr("paused") == 'no') {
			force.stop(); 
			d3.selectAll(".node").attr("fixed", function (d) {
				d.fixed = 1;
			});
			d3.select("#stop-layout").attr("paused", 'yes')
		} else {
			d3.selectAll(".node").attr("fixed", function (d) {
				d.fixed = 0;
			});
			force.start();
			d3.select("#stop-layout").attr("paused", 'no')
		}
	});*/

    if (text_present) {
        // Adds an anchor element around each appellation's text-position.
        var add_appellation = function(node, item) {
            try {
                var range = rangy.createRange();
                range.setStart(node.firstChild, item.textposition.startposition);
                range.setEnd(node.firstChild, item.textposition.endposition);

                var highlightNode = document.createElement('a');
                highlightNode.className = 'appellation';
                highlightNode.id = item.id;
                highlightNode.style.color = color(types[item.type]);
                range.surroundContents(highlightNode);
            } catch (err) {
                // Ignore appellations that ignore with those already added to the text.
                //  (handles cases wehre Rangy gets confused)
            }
        }

        // The /networks/appellations/ endpoint provides data for a specific text.
        $.get("/networks/appellations/"+text_id+"/", function(data) {
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
                    activate_edge(relations_lookup[relations_predicates[e.target.id]], Array(e.target));
                } else {
                    activate_node(appellations_lookup[e.target.id], [e.target]);
                }
            });
        
            // An 'active' node may have been passed from another page. If so, activate it.
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
        });
    }


	// Clears all 'focal' classes from nodes, edges, appellations.
	function deselect_all() {
		// De-select all
		d3.select(".node.focal")
		    .classed("focal", false)
			.attr("r", 10);	
			
		link.classed("focal", false);
		d3.select('a.appellation.focal').classed("focal", false)	
			
	}

	// Highlights node, and corresponding appellations.
	//	intext is a list of appellation elements in the text.	
	function activate_node(d, intext) {
		d.fixed = 1;
		deselect_all();

		// Select the focal node
		d.focal = true;
		d3.select(".node[id=\"" + d.id + "\"]")
			.classed("focal", true)
			.attr("r", 15);
		
		if (text_present) {
            intext.forEach( function(i) {
                console.log(i);
                if (i) {    // Not all appellations are found in this text.
                    d3.select('a[id="' + i.id + '"]').classed("focal", true);
                }
            });
        }
        		
		show_node_details(d);
	}
	
	// Highlights edge, and corresponding appellations.
	//	intext is a list of appellation elements in the text.
	function activate_edge(d, intext) {
		deselect_all();

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
                
            var texts = {};
            data.appellations.forEach( function(a) {
                if (! texts[a.textposition.text] ){
                    texts[a.textposition.text] = a.textposition;
                }
            });
        
            var values = Object.keys(texts).map(function(key){
                return texts[key];
            });
    
            $('.element_texts_title').text('Concept appears in...');
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
	}
	
	function show_edge_details(d) {
        $('div[id="instructions"]').empty();
		d3.select('.element_details_title').text(d.source.label + ' [' + d.label + '] ' + d.target.label);
		d3.select('.element_details_uri').text(d.concept);
        show_edge_texts(d);
	}
});