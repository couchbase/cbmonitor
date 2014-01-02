/*jshint jquery: true, browser: true*/
/*global d3: true, Spinner: true*/

function drawBase(actualSize) {
    "use strict";

    d3.select("#chart").append("svg").attr({
        height: actualSize, width: actualSize
    });

    d3.select("svg").append("rect").attr({
        height: actualSize,
        width: actualSize,
        fill: "#51a351",
        stroke: 'white'
    });
}

function drawRectangles(matrix, columns, rectSize, actualSize) {
    "use strict";

    var cursorOffset = 10,
        digitsAfterPoint = 4;

    var scale = d3.scale.linear()
                        .domain([0, 1])
                        .range([0, rectSize]);

    d3.select("svg").selectAll('g')
        .data(matrix)
        .enter()
        .append('g').selectAll('rect')
            .data(function(d) { return d; })
            .enter()
            .append('rect')
            .on("mouseover", function(d, i, j) {
                var xPos = cursorOffset + rectSize * (i + 1) - actualSize / 2;
                var yPos = cursorOffset + rectSize * (j + 1);

                d3.select("#tooltip")
                    .style("left", xPos + "px")
                    .style("top", yPos + "px")
                    .select("#corr")
                    .text(d.toFixed(digitsAfterPoint));
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
            })
            .transition()
            .duration(1000)
            .ease('linear')
            .each('start', function() {
                d3.select(this).attr({
                    fill: '#51a351',
                    height: 0,
                    width: 0
                });
            })
            .attr({
                x: function(corr, i) {
                    return scale(i + 0.5 * (1 - Math.abs(corr)));
                },
                y: function(corr, i, j) {
                    return scale(j + 0.5 * (1 - Math.abs(corr)));
                },
                fill: function(corr) {
                    return (corr > 0)? "white" : "#f89406";
                },
                height: function(corr) {
                    return scale(Math.abs(corr));
                },
                width: function(corr) {
                    return scale(Math.abs(corr));
                }
            });

}

function startSpinner(maxSize) {
    "use strict";

    var spinner = new Spinner({
        lines: 7,
        length: 5,
        width: 10,
        radius: 30,
        corners: 0.5,
        color: 'white',
        top: maxSize / 2 - 100
    }).spin(document.getElementById('spinner'));

    return spinner;
}

$(document).ready(function(){
    "use strict";

    var maxSize = screen.availHeight * 0.95;

    var spinner = startSpinner(maxSize);

    var snapshot = $("meta[property='snapshot']")[0].getAttribute("value"),
        url = "/reports/get_corr_matrix/?snapshot=" + snapshot;

    d3.xhr(url, "json", function(xhr) {
        spinner.stop();
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
