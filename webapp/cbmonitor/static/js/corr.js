/*jshint jquery: true, browser: true*/
/*global d3: true*/

function drawBase(shape) {
    "use strict";

    var maxSize = 650,
        rectSize = Math.floor(maxSize / shape),
        actualSize = rectSize * shape;

    d3.select("#chart").append("svg").attr({
        height: actualSize, width: actualSize
    });

    d3.select("svg").append("rect").attr({
        height: actualSize, width: actualSize, fill: "#808080"
    });

    return rectSize;
}

$(document).ready(function(){
    "use strict";

    var snapshot = $("meta[property='snapshot']")[0].getAttribute("value"),
        url = "/cbmonitor/get_corr_matrix/?snapshot=" + snapshot;

    d3.xhr(url, "json", function(xhr) {
        var data = JSON.parse(xhr.response),
            matrix = data.matrix,
            columns = data.columns,
            shape = matrix.length;

        var rectSize = drawBase(shape);

        d3.select("svg").selectAll('g')
            .data(matrix)
            .enter()
            .append('g').selectAll('rect')
                .data(function(d) { return d; })
                .enter()
                .append('rect').attr({
                    x: function(corr, i, j) {
                        var weight = Math.sqrt(Math.abs(corr));
                        return rectSize * (i + 0.5 * (1 - weight));
                    },
                    y: function(corr, i, j) {
                        var weight = Math.sqrt(Math.abs(corr));
                        return rectSize * (j + 0.5 * (1 - weight));
                    },
                    fill: function(d, i, j) {
                        return (d > 0)? "white" : "black";
                    },
                    height: function(corr) {
                        return Math.sqrt(Math.abs(corr)) * rectSize;
                    },
                    width: function(corr) {
                        return Math.sqrt(Math.abs(corr)) * rectSize;
                    }
                });
    });
});
