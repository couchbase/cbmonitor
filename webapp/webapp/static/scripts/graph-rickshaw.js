"use strict";


var GRAPH = GRAPH || {};  // namespace


/*
 ******************************************************************************
 ******************************************************************************
 */
GRAPH.GraphManager = function(args) {
    this.data = args.data;
    this.metrics = args.metrics;
    this.seriesly = args.seriesly;
};


GRAPH.GraphManager.prototype.init = function() {
    var dataHandler = new GRAPH.DataHandler(this.data);
    var series_data = dataHandler.prepareSeries(this.metrics);
    var palette = new Rickshaw.Color.Palette();
    var series = [];
    for(var i = 0, len = this.metrics.length; i < len; i++) {
        series.push({
            data: series_data[i],
            name: this.metrics[i],
            color: palette.color()});
    }
    this.graph = new Rickshaw.Graph( {
        element: document.querySelector("#chart"),
        width: 800,
        height: 400,
        series: series
    });
    this.graph.render();
};


GRAPH.GraphManager.prototype.setupLegend = function() {
    var legend = new Rickshaw.Graph.Legend( {
        element: document.querySelector('#legend'),
        graph: this.graph
    });
    var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
        graph: this.graph,
        legend: legend
    });
};


GRAPH.GraphManager.prototype.setupAxes = function() {
    var y_axis = new Rickshaw.Graph.Axis.Y({
        graph: this.graph,
        orientation: 'left',
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        element: document.getElementById('y_axis')
    });
    y_axis.render();
    var x_axis = new Rickshaw.Graph.Axis.Time({
        graph: this.graph
    });
    x_axis.render();
};


GRAPH.GraphManager.prototype.setupTips = function() {
    var hoverDetail = new Rickshaw.Graph.HoverDetail( {
        graph: this.graph
    });
};


GRAPH.GraphManager.prototype.setupSlider = function() {
    var slider = new GRAPH.RangeSlider( {
        graph: this.graph,
        element: $('#slider'),
        metrics: this.metrics,
        seriesly: this.seriesly
    });
};

/*
 ******************************************************************************
 ******************************************************************************
 */

GRAPH.DataHandler = function(data) {
    this.data = data;
    this.timestamps = this.prepareTimestamps();
};


GRAPH.DataHandler.prototype.prepareTimestamps = function() {
    var timestamps = [];
    for(var timestamp in this.data) {
        if (this.data.hasOwnProperty(timestamp)) {
            timestamps.push(parseInt(timestamp, 10));
        }
    }
    return timestamps.sort();
};


GRAPH.DataHandler.prototype.prepareSeries = function(metrics) {
    var i, len, timestamp,
        series = [];
    for(i = 0, len = metrics.length; i < len; i++) {
        series.push([]);
    }
    for(i = 0, len = this.timestamps.length; i < len; i++) {
        timestamp = this.timestamps[i];
        for(var j = 0, lenOfMetrics = metrics.length; j < lenOfMetrics; j++) {
            series[j].push({
                x: timestamp / 1000,
                y: this.data[timestamp][j]
            });
        }
    }
    return series;
};

/*
 ******************************************************************************
 ******************************************************************************
 */

GRAPH.RangeSlider = function(args) {
    var element = args.element;
    var graph = args.graph;
    var metrics = args.metrics;
    var seriesly = args.seriesly;

    $(function() {
        $(element).slider( {
            range: true,
            min: graph.dataDomain()[0],
            max: graph.dataDomain()[1],
            values: [
                graph.dataDomain()[0],
                graph.dataDomain()[1]
            ],
            stop: function(event, ui) {
                var url = seriesly.biuldURL(
                    "1000", metrics, ui.values[0] * 1000, ui.values[1] * 1000
                );
                $.ajax({url: url, dataType: "json", success: function(data){
                    var dataHandler = new GRAPH.DataHandler(data);
                    var series = dataHandler.prepareSeries(metrics);

                    for(var i = 0, len = graph.series.length; i < len; i++) {
                        graph.series[i].data = series[i];
                    }
                    graph.update();
                }});
            }
        });
    });
    element[0].style.width = graph.width + 'px';
};
