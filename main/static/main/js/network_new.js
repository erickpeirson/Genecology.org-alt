// Disable text-specific functionality.
var text_present = false;

// Brings an element to the top of the display.
d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};

d3.selection.prototype.moveEdgeToFront = function () {
       
};

// Wraps a text label to maintain a given width.
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

// When the user hovers over a node, the node and its label should be magnified.
var mouseenter_node = function(e) {
    d = e.target;   // Element over which the user hovered.
    d3.select('.node[id="'+d.id+'"]')   // Node.
        .attr('r', nodeSize*2)
        .classed("hovered", true);        
    d3.select('.label[id="'+d.id+'"]')  // Label.
        .classed("hovered", true);
    
    // In and out edges should be emphasized.
    d3.selectAll('.indirect_hover').classed('indirect_hover', false);
    d3.selectAll('[source="'+d.id+'"]')
        .classed('indirect_hover', true)
        .moveToFront();
    d3.selectAll('[target="'+d.id+'"]')
        .classed('indirect_hover', true)
        .moveToFront();
}

// When the user stops hovering over a node, the node should return to its
//  default appearance.
var mouseexit_node = function(e) {
    d = e.target;   // Element over which the user hovered.
    var hovered_node = d3.select('.node[id="'+d.id+'"]');
    hovered_node.attr('r', function(d) {
            if (hovered_node.classed('focal')) {
                return nodeSize*2;  // TODO: this should be more flexible.
            } else {
                return nodeSize;
            }
        })
        .classed("hovered", false);        
    d3.select('.label[id="'+d.id+'"]')
        .classed("hovered", false);            
}

var mouseenter_edge = function(e) {
    d = e.target;
    var hovered_edge = d3.select('line[id="'+d.id+'"]');
    hovered_edge.classed('hover', true);   
};

var mouseexit_edge = function(e) {
    d = e.target;
    d3.select('line[id="'+d.id+'"]')
        .classed('hover', false);
};

function redraw() {
    svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
}

var node_drag = d3.behavior.drag()
    .on("dragstart", dragstart)
    .on("drag", dragmove)
    .on("dragend", dragend); 
    
function dragstart(d, i) {
    // Maybe we'll need this later?
}

function dragmove(d, i) {
    // Move the nodes along with the dragging.
    d.px += d3.event.dx;
    d.py += d3.event.dy;
    d.x += d3.event.dx;
    d.y += d3.event.dy; 
}

function dragend(d, i) {
    // Maybe we'll need this later?
}     

// Call before activating/selecting nodes or edges.
function deselect_all() {
    d3.selectAll('.node.focal').attr("r", nodeSize);
    d3.selectAll('.focal').classed('focal', false);
    d3.selectAll('.node_active').classed('node_active', false);
}

// When the user clicks on an edge...
var edge_click = function(d) {
    activate_edge(d);  // Activate the edge.
}

var node_click = function (d) {		  // User clicks a node in the network.
    activate_node(d);
}   

function show_node_details(d) {
    $('div[id="instructions"]').empty();
    d3.select('.element_details_title').text(d.label);
    //    show_node_texts(d);
    
    d3.select('.element_app_texts_title').text('Node appears in...');
    console.log(d);
    d3.json(app_list_url+"?interpretation="+d.concept, function(error, appellations) {
        console.log(appellations);
        d3.select('.element_app_texts_list')
            .selectAll('li')
            .data(appellations.results)
            .enter()
                .append('li')
                .append('a')
                .attr('href', function(t) { return '/text/'+t.text.id+'/?node='+d.id; })                    
                .html(function(d) { return d.text.label.slice(0,50)+'...'; });
        
    });
    
    
    d3.select('.element_texts_title').text('Texts by this node...');
    d3.json(text_list_url+"?creators="+d.concept, function(error, texts) {
        console.log(texts);
        d3.select('.element_texts_list')
            .selectAll('li')
            .data(texts.results)
            .enter()
                .append('li')
                .append('a')
                .attr('href', function(t) { return '/text/'+t.id+'/?node='+d.id; })                
                .html(function(d) { return d.label.slice(0,50)+'...'; });
        
    });

}

// Highlight the edge!
function activate_edge(d) {
    deselect_all(); // Clears out previous focal selections.
    
    // Make the targeted edge display as focal.
    d3.select('line[id="' + d.id + '"]').classed("focal", true);
    
    // Make the source and target nodes display as focal.
    d3.select('.node[id="' + d.source_id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);
    d3.select('.node[id="' + d.target_id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);    
        
    // Make the source and target node labels display as focal
    d3.select('.label[id="' + d.target_id + '"]').classed("focal", true);
    d3.select('.label[id="' + d.source_id + '"]').classed("focal", true);

    // Bring source and target nodes to the top.
    d3.select('g[id="' + d.source_id + '"]').moveToFront();
    d3.select('g[id="' + d.target_id + '"]').moveToFront();

    // Bookkeeping... 
    d.focal = true; 
    active_edge = d.id;
}

function activate_node(d, intext) {
    deselect_all();

    // Select the focal node, and bring it to the front.
    d3.select('.label[id="' + d.id + '"]').classed("focal", true);    
    d3.select('.node[id="' + d.id + '"]').classed("focal", true)
        .attr("r", nodeSize*2);
    d3.select('g[id="' + d.id + '"]').moveToFront();

    show_node_details(d);
    active_node = d.id;
    
    // In and out edges should be emphasized.
    d3.selectAll('.node_active').classed('node_active', false);
    d3.selectAll('[source="'+d.id+'"]')
        .classed('node_active', true)
        .moveToFront();
    d3.selectAll('[target="'+d.id+'"]')
        .classed('node_active', true)
        .moveToFront();        
            
}

