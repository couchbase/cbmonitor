"use strict";


var GRAPH = GRAPH || {};  // namespace


GRAPH.Graph = function(seriesly) {
    this.redraw_overview = true;
    this.seriesly = seriesly;
    this.labels = [];

    this.options = {
        xaxis: {mode: "time", tickLength: 5},
        yaxis: {min: 0},
        selection: {mode: "x"},
        points: {"show": true, "radius": 1.5},
        grid: {hoverable: true, markings: []}
    };
    this.defineBindings();
};


GRAPH.Graph.prototype.defineBindings = function() {
    var that = this,
        placeholder = $("#placeholder"),
        overview = $("#overview");

    placeholder.bind("plotselected", function (event, ranges) {
        var from = Math.ceil(ranges.xaxis.from),
            to = Math.floor(ranges.xaxis.to),
            group = Math.round((to - from) / 100);
        that.redraw_overview = false;
        that.seriesly.query(group.toString(), that.labels, from, to, that);
        that.overview.setSelection(ranges, true);
    });

    overview.bind("plotselected", function (event, ranges) {
        that.plot.setSelection(ranges);
    });

    placeholder.bind("plothover", function (event, pos, item) {
        var tooltip = $("#tooltip");
        if (item) {
            tooltip.remove();
            that.showTooltip(item);
        } else {
            tooltip.remove();
        }
    });
};


GRAPH.Graph.prototype.addMetric = function(group, label) {
    this.redraw_overview = true;
    this.labels.push(label);
    this.seriesly.query(group, this.labels, null, null, this);
};


GRAPH.Graph.prototype.handleData = function(data) {
    var i, len;
    this.data = [];

    // reset chart data
    for(i = 0, len = this.labels.length; i < len; i++) {
        this.data.push({data: [], label: this.labels[i]});
    }
    // populate chart_data
    for(var timestamp in data) {
        if (data.hasOwnProperty(timestamp)) {
            for(i = 0, len = this.labels.length; i < len; i++) {
                this.data[i].data.push([timestamp, data[timestamp][i]]);
            }
        }
    }
    this.draw();
};


GRAPH.Graph.prototype.draw = function() {
    // draw overview chart
    if (this.redraw_overview) {
        this.overview = $.plot($("#overview"), this.data, {
            xaxis: {mode: "time"},
            yaxis: {min: 0, autoscaleMargin: 0.1},
            selection: {mode: "x"},
            points: {"show": true, radius: 1}
        });
    }
    // draw main chart
    this.plot = $.plot($("#placeholder"), this.data, this.options);
};


GRAPH.Graph.prototype.showTooltip = function(item) {
    var y = item.datapoint[1].toFixed(2);
    $('<div id="tooltip">' + y + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: item.pageY + 10,
        left: item.pageX + 10,
        border: '1px solid #000',
        padding: '4px',
        borderRadius: '4px',
        'background-color': '#fff',
        opacity: 0.70
    }).appendTo("body").fadeIn(200);
};
