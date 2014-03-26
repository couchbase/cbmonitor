/*jshint jquery: true, browser: true*/
/*global d3: true, Spinner: true*/


var MVMNTS = {
    max_h: window.innerHeight - 25,
    max_w: window.innerWidth - 25,
    placeholder: 40,
    min_bar_h: 20,
    grid_width: 100,
    legend_w: 170,
    node_w: 135,
    tooltip_margin: 50,
    palette: [
        "#51A351",
        "#F89406",
        "#7D1935",
        "#4A96AD",
        "#DE1B1B",
        "#E9E581",
        "#A2AB58",
        "#FFE658",
        "#118C4E",
        "#193D4F"
    ]
};


function drawBase() {
    "use strict";

    d3.select("body")
        .on("keydown", function() {
            if (d3.event.which === 27) {
                d3.select("#tooltip").classed("hidden", true);
            }
        })
        .on("click", function() {
            d3.select("#tooltip").classed("hidden", true);
        });

    d3.select("#chart")
        .append("svg")
        .attr({
            height: MVMNTS.max_h + 2,
            width: MVMNTS.max_w + 2
        })
        .append("rect")
        .attr({
            x: MVMNTS.placeholder,
            y: 0,
            width: MVMNTS.max_w - MVMNTS.placeholder,
            height: MVMNTS.max_h,
            "fill-opacity": 0,
            stroke: "black",
            "shape-rendering": "crispEdges"
        });
}


function drawNodes(large_span_h, src_nodes, movements_per_dest) {
    "use strict";

    var dest_nodes = Object.keys(movements_per_dest);

    d3.select("svg").append("g").selectAll("rect")
        .data(src_nodes)
        .enter()
        .append("rect")
        .attr({
            x: 0,
            y: function(node, i) {
                var offset = 0;
                for (var j= 0; j < i; j++) {
                    if (dest_nodes.indexOf(src_nodes[j]) !== -1) {
                        offset += large_span_h;
                    } else {
                        offset += MVMNTS.min_bar_h;
                    }
                }
                return offset;
            },
            height: function(node) {
                if (dest_nodes.indexOf(node) !== -1) {
                    return large_span_h;
                } else {
                    return MVMNTS.min_bar_h;
                }
            },
            width: MVMNTS.placeholder,
            fill: function(node, i) { return MVMNTS.palette[i]; },
            stroke: "white",
            rx: 7
        });

    d3.select("svg").append("g").selectAll("line")
        .data(src_nodes)
        .enter()
        .append("line")
        .attr({
            x1: MVMNTS.placeholder,
            y1: function(node, i) {
                var offset = 0;
                for (var j= 0; j < i; j++) {
                    if (dest_nodes.indexOf(src_nodes[j]) !== -1) {
                        offset += large_span_h;
                    } else {
                        offset += MVMNTS.min_bar_h;
                    }
                }
                return offset;
            },
            y2: function(node, i) {
                var offset = 0;
                for (var j= 0; j < i; j++) {
                    if (dest_nodes.indexOf(src_nodes[j]) !== -1) {
                        offset += large_span_h;
                    } else {
                        offset += MVMNTS.min_bar_h;
                    }
                }
                return offset;
            },
            x2: MVMNTS.max_w,
            stroke: "black",
            "shape-rendering": "crispEdges",
            "stroke-dasharray": "5,5"
        });

    d3.select("svg").append("g").selectAll("rect")
        .data(src_nodes)
        .enter()
        .append("rect")
        .attr({
            x: MVMNTS.placeholder,
            y: function(node, i) {
                var offset = 0;
                for (var j= 0; j < i; j++) {
                    if (dest_nodes.indexOf(src_nodes[j]) !== -1) {
                        offset += large_span_h;
                    } else {
                        offset += MVMNTS.min_bar_h;
                    }
                }
                if (dest_nodes.indexOf(node) !== -1 ) {
                    offset += large_span_h - MVMNTS.min_bar_h;
                }
                return offset;
            },
            height: MVMNTS.min_bar_h,
            width: MVMNTS.node_w,
            fill: "white",
            stroke: "black",
            "shape-rendering": "crispEdges"
        });

    d3.select("svg").append("g").selectAll("text")
        .data(src_nodes)
        .enter()
        .append("text")
        .attr({
            x: MVMNTS.placeholder + 5,
            y: function(node, i) {
                var offset = -5;
                for (var j = 0; j < i; j++) {
                    if (dest_nodes.indexOf(src_nodes[j]) !== -1) {
                        offset += large_span_h;
                    } else {
                        offset += MVMNTS.min_bar_h;
                    }
                }
                if (dest_nodes.indexOf(node) !== -1) {
                    offset += large_span_h;
                } else {
                    offset += MVMNTS.min_bar_h;
                }
                return offset;
            },
            "font-size": 14
        })
        .text(function(node) {
            var movements = movements_per_dest[node] || 0;
            return node + ": " + movements;
        });
}


function drawMovements(data, large_span_height) {
    "use strict";

    var scale = d3.scale.linear()
                        .domain([0, data.max_ts - data.min_ts])
                        .range([0, MVMNTS.max_w - MVMNTS.placeholder]);
    var dest_nodes = Object.keys(data.movements_per_dest);

    d3.select("svg").append("g").selectAll("g")
        .data(data.src_nodes)
        .enter()
        .append("g").selectAll("rect")
            .data(function(node) {
                if (dest_nodes.indexOf(node) !== -1) {
                    return Object.keys(data.movements[node]);
                } else {
                    return [];
                }
            })
            .enter()
            .append("rect")
            .on("click", function(vbucket) {
                var profiles = data.bars[vbucket][4],
                    hotspots = $("#hotspots");
                hotspots.empty();
                for (var i = 0; i < profiles.length; i++) {
                    var ratio = profiles[i][2].toFixed(2);
                    hotspots.append(
                        "<tr>" +
                            "<td class='hotspot'>" + profiles[i][0] + " -> " + profiles[i][1] + "</td>" +
                            "<td class='value'>" + ratio + "</td>" +
                            "<td class='bar' style='background: -webkit-linear-gradient(left, #D9534F "+ ratio +"%, #FFFFFF 1%)'></td>" +
                        "</tr>"
                    );
                }
                var header = "vbucket: " + vbucket + ", total time: " + data.bars[vbucket][1].toFixed(1) + " seconds";
                d3.select("#tooltip").select("#header").text(header);
                d3.select("#tooltip").style("top", MVMNTS.tooltip_margin + "px");
                d3.select("#tooltip").classed("hidden", false);
                d3.event.stopPropagation();
            })
            .attr({
                x: function(vbucket) {
                    return scale(data.bars[vbucket][0]) + MVMNTS.placeholder;
                },
                y: function(vbucket, vbi, j) {
                    var concurrency = data.concurrency_per_dest[data.src_nodes[j]];
                    var h = large_span_height / concurrency;
                    var offset = 0;
                    for (var i = 0; i < j; i++) {
                        if (dest_nodes.indexOf(data.src_nodes[i]) !== -1) {
                            offset += large_span_height;
                        } else {
                            offset += MVMNTS.min_bar_h;
                        }
                    }
                    return offset + data.bars[vbucket][2] * h;
                },
                height: function(vbucket, i, j) {
                    var concurrency = data.concurrency_per_dest[data.src_nodes[j]];
                    return large_span_height / concurrency;
                },
                width: function(vbucket) {
                    return scale(data.bars[vbucket][1]);
                },
                fill: function(vbucket) {
                    return data.bars[vbucket][3];
                },
                stroke: "black",
                "shape-rendering": "crispEdges"
            });
}


function drawGrid() {
    "use strict";

    var grid = [];
    for (var i = MVMNTS.placeholder; i < MVMNTS.max_w; i+=MVMNTS.grid_width) {
        grid.push(i);
    }

    d3.select("svg").append("g").selectAll("line")
        .data(grid)
        .enter()
        .append("line")
        .attr({
            x1: function(d) { return d; },
            y1: 0,
            x2: function(d) { return d; },
            y2: MVMNTS.max_h,
            stroke: "black",
            "shape-rendering": "crispEdges",
            "stroke-dasharray": "5,5"
        });
}


function drawLegend(rebalance_t) {
    "use strict";

    d3.select("svg").append("g")
        .append("rect")
        .attr({
            x: MVMNTS.max_w - MVMNTS.legend_w,
            y: 0,
            height: MVMNTS.min_bar_h,
            width: MVMNTS.legend_w,
            fill: "white",
            stroke: "black",
            "shape-rendering": "crispEdges"
        });

    d3.select("svg").append("g").append("text")
        .attr({
            x: MVMNTS.max_w - MVMNTS.legend_w + 5,
            y: 15,
            "font-size": 14
        })
        .text("Total duration: " + rebalance_t.toFixed(1) +" min");
}


$(document).ready(function(){
    "use strict";

    var filename = $("meta[property='filename']")[0].getAttribute("value"),
        url = "/reports/get_movements/?filename=" + filename;

    d3.xhr(url, "json", function(xhr) {
        var data = JSON.parse(xhr.response);

        var num_large_spans = Object.keys(data.movements_per_dest).length,
            num_small_spans = data.src_nodes.length - num_large_spans,
            large_span_h = (MVMNTS.max_h - num_small_spans * MVMNTS.min_bar_h) / num_large_spans,
            rebalance_t = (data.max_ts - data.min_ts) / 60;

        drawBase();
        drawGrid();
        drawMovements(data, large_span_h);
        drawNodes(large_span_h, data.src_nodes, data.movements_per_dest);
        drawLegend(rebalance_t);
    });
});
