/*jshint jquery: true, browser: true*/
/*global d3: true, nv: true*/

/*
 * Name space
 */
var GRAPH = GRAPH || {};

GRAPH.GraphManager = function(args) {
    "use strict";

    this.metrics = args.metrics;
    this.container = args.container;
};

GRAPH.GraphManager.prototype.init = function(data) {
    "use strict";

    var dataHandler = new GRAPH.DataHandler(data),
        series_data = dataHandler.prepareSeries(this.metrics),
        container = "#" + this.container + " svg";

    var format = d3.time.format("%H:%M:%S");
    nv.addGraph(function() {
        var chart = nv.models.lineWithFocusChart();

        chart.xAxis
            .tickFormat(format);
        chart.x2Axis
            .tickFormat(format);
        chart.yAxis
            .tickFormat(d3.format(',.2s'));
        chart.y2Axis
            .tickFormat(d3.format(',.2s'));

        d3.select(container)
            .datum(series_data)
            .call(chart);

        return chart;
    });
};

GRAPH.DataHandler = function(data) {
    "use strict";

    this.data = data;
    this.timestamps = this.prepareTimestamps();
};


GRAPH.DataHandler.prototype.prepareTimestamps = function() {
    "use strict";

    var timestamps = [];
    for(var timestamp in this.data) {
        if (this.data.hasOwnProperty(timestamp)) {
            timestamps.push(parseInt(timestamp, 10));
        }
    }
    return timestamps.sort();
};


GRAPH.DataHandler.prototype.prepareSeries = function(metrics) {
    "use strict";

    var i, j,
        len, len_metrics,
        timestamp,
        series = [];
    for(i = 0, len = metrics.length; i < len; i++) {
        series.push({
            key: metrics[i],
            values: []
        });
    }

    for(i = 0, len = this.timestamps.sort().length; i < len; i++) {
        timestamp = this.timestamps[i];
        for(j = 0, len_metrics = metrics.length; j < len_metrics; j++) {
            series[j].values.push({
                x: timestamp,
                y: this.data[timestamp][j]
            });
        }
    }
    return series;
};
