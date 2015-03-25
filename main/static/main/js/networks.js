var width = 600,
    height = 500;

var svg = d3.select('#network-visualization').append('svg')
    .attr('width', width)
    .attr('height', height);

d3.json('