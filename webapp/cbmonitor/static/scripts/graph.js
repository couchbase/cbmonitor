/*jshint jquery: true, browser: true*/
/*global d3: true, nv: true, SERIESLY: true*/

/*
 * Name space
 */
var GRAPH = GRAPH || {};

GRAPH.buildPointer = function(ui) {
    "use strict";

    var type = ui.draggable.attr("type"),
        cluster = ui.draggable.attr("cluster"),
        server = ui.draggable.attr("server"),
        bucket = ui.draggable.attr("bucket"),
        item = ui.draggable.text();

    var ptr = type + "/" + cluster + "/";
    if (bucket.length > 0) {
        ptr += bucket + "/";
    }
    if (server.length > 0) {
        ptr += server + "/";
    }
    return ptr + item;
};

GRAPH.GraphManager = function() {
    "use strict";

    this.seriesly = new SERIESLY.Seriesly("cbmonitor");
    this.metrics = {};
};

GRAPH.GraphManager.prototype.init = function(data) {
    "use strict";

    var dataHandler = new GRAPH.DataHandler(data),
        series_data = dataHandler.prepareSeries(this.metrics[this.container]),
        container = "#" + this.container + " svg";

    var format = d3.time.format("%H:%M:%S");
    nv.addGraph(function() {
        var chart = nv.models.lineWithFocusChart().forceY([0]);

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

GRAPH.GraphManager.prototype.plot = function(container, ui) {
    "use strict";

    var new_metric = ui.draggable.text();

    if (this.metrics[container] === undefined) {
        this.metrics[container] = [new_metric];
        this.ptrs = [GRAPH.buildPointer(ui)];
    } else if (this.metrics[container].indexOf(new_metric) === -1) {
        this.metrics[container].push(new_metric);
        this.ptrs.push(GRAPH.buildPointer(ui));
    }
    this.container = container;

    this.seriesly.query({
        group: 1000,
        ptrs: this.ptrs,
        callback_object: this
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
