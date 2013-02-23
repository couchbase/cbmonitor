/*jshint jquery: true, browser: true*/
/*global d3: true, nv: true, SERIESLY: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.buildPointer = function(ui) {
    "use strict";

    var cluster = ui.draggable.attr("cluster"),
        server = ui.draggable.attr("server"),
        bucket = ui.draggable.attr("bucket"),
        item = ui.draggable.text();

    var ptr = "&ptr=/samples/" + item + "&reducer=avg";

    var filter = "&f=/meta/cluster&fv=" + cluster;
    filter += "&f=/meta/bucket&fv="; filter += bucket.length ? bucket : "none";
    filter += "&f=/meta/server&fv="; filter += server.length ? server : "none";

    return ptr + filter;
};

CBMONITOR.GraphManager = function() {
    "use strict";

    this.seriesly = new SERIESLY.Seriesly("cbmonitor");
    this.metrics = {};
};

CBMONITOR.GraphManager.prototype.init = function(data) {
    "use strict";

    var dataHandler = new CBMONITOR.DataHandler(data),
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

CBMONITOR.GraphManager.prototype.plot = function(container, ui) {
    "use strict";

    var new_metric = ui.draggable.text();

    if (this.metrics[container] === undefined) {
        this.metrics[container] = [new_metric];
        this.ptrs = [CBMONITOR.buildPointer(ui)];
    } else if (this.metrics[container].indexOf(new_metric) === -1) {
        this.metrics[container].push(new_metric);
        this.ptrs.push(CBMONITOR.buildPointer(ui));
    }
    this.container = container;

    var chart_data = [];
    for(var i = 0, l = this.ptrs.length; i < l; i++) {
        chart_data.push(
            this.seriesly.query({group: 1000, ptr: this.ptrs[i]})
        );
    }
    this.init(chart_data);
};

CBMONITOR.GraphManager.prototype.clear = function() {
    "use strict";

    this.metrics = {};
    $("#first_view").empty().append("<svg>");
    $("#second_view").empty().append("<svg>");
    $("#second_view_double").empty().append("<svg>");
    $("#third_view").empty().append("<svg>");
    $("#fourth_view").empty().append("<svg>");
};

CBMONITOR.DataHandler = function(data) {
    "use strict";

    this.data = data;
    this.timestamps = this.prepareTimestamps();
};

CBMONITOR.DataHandler.prototype.prepareTimestamps = function(dataset) {
    "use strict";

    var timestamps = [];
    for(var timestamp in dataset) {
        if (dataset.hasOwnProperty(timestamp)) {
            timestamps.push(parseInt(timestamp, 10));
        }
    }
    return timestamps.sort();
};

CBMONITOR.DataHandler.prototype.prepareSeries = function(metrics) {
    "use strict";

    var timestamp, timestamps, values,
        series = [];
    for(var i = 0, lenm = metrics.length; i < lenm; i++) {
        timestamps = this.prepareTimestamps(this.data[i]);
        values = [];
        for(var j = 0, lent = timestamps.length; j < lent; j++) {
            timestamp = timestamps[j];
            values.push({
                x: timestamp,
                y: this.data[i][timestamp]
            });
        }
        series.push({
            key: metrics[i],
            values: values
        });
    }
    return series;
};
