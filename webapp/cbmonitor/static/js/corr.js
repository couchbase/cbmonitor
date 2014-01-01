/*jshint jquery: true, browser: true*/
/*global d3: true*/

function drawBase(actualSize) {
    "use strict";

    d3.select("#chart").append("svg").attr({
        height: actualSize, width: actualSize
    });

    d3.select("svg").append("rect").attr({
        height: actualSize, width: actualSize, fill: "#51a351"
    });
}

function drawRectangles(matrix, columns, rectSize, actualSize) {
    "use strict";

    var cursorOffset = 10,
        scaleSqrt = d3.scale.sqrt()
                            .domain([0, 1])
                            .range([0, rectSize]),
        scaleLinear = d3.scale.linear()
                              .domain([0, 1])
                              .range([0, rectSize]);

    d3.select("svg").selectAll('g')
        .data(matrix)
        .enter()
        .append('g').selectAll('rect')
            .data(function(d) { return d; })
            .enter()
            .append('rect').attr({
                x: function(corr, i) {
                    return scaleLinear(i + 0.5) - 0.5 * scaleSqrt(Math.abs(corr));
                },
                y: function(corr, i, j) {
                    return scaleLinear(j + 0.5) - 0.5 * scaleSqrt(Math.abs(corr));
                },
                fill: function(d, i, j) {
                    return (d > 0)? "white" : "#f89406";
                },
                height: function(corr) {
                    return scaleSqrt(Math.abs(corr));
                },
                width: function(corr) {
                    return scaleSqrt(Math.abs(corr));
                }
            })
            .on("mouseover", function(d, i, j) {
                var xPos = cursorOffset + rectSize * (i + 1) - actualSize / 2;
                var yPos = cursorOffset + rectSize * (j + 1);

                d3.select("#tooltip")
                    .style("left", xPos + "px")
                    .style("top", yPos + "px")
                    .select("#corr")
                    .text(d.toFixed(4));
                d3.select("#tooltip")
                    .select("#x")
                    .text(columns[i]);
                d3.select("#tooltip")
                    .select("#y")
                    .text(columns[j]);
                d3.select("#tooltip").classed("hidden", false);
            })
            .on("mouseout", function() {
                d3.select("#tooltip").classed("hidden", true);
            });

}

$(document).ready(function(){
    "use strict";

    var maxSize = 650;

    var snapshot = $("meta[property='snapshot']")[0].getAttribute("value"),
        url = "/reports/get_corr_matrix/?snapshot=" + snapshot;

    d3.xhr(url, "json", function(xhr) {
        var data = JSON.parse(xhr.response),
            matrix = data.matrix,
            columns = data.columns,
            shape = matrix.length;

        var rectSize = Math.floor(maxSize / shape),
            actualSize = rectSize * shape;

        drawBase(actualSize);
        drawRectangles(matrix, columns, rectSize, actualSize);
    });
});
