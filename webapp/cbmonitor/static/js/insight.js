/*jshint jquery: true, browser: true*/
/*global angular, d3*/

angular.module("insight", [])
    .config(["$interpolateProvider", function ($interpolateProvider) {
        "use strict";

        $interpolateProvider.startSymbol("[[");
        $interpolateProvider.endSymbol("]]");
    }]);


var INSIGHT = INSIGHT || {};

INSIGHT.palette = [
    "#f89406",
    "#51A351",
    "#7D1935",
    "#4A96AD",
    "#DE1B1B",
    "#E9E581",
    "#A2AB58",
    "#FFE658",
    "#118C4E",
    "#193D4F"
];

INSIGHT.height = 548;
INSIGHT.width = 900;

function Insights($scope, $http) {
    "use strict";

    $scope.getOptions = function() {
        $scope.inputs = [];
        $scope.abscissa = null;
        $scope.vary_by = null;
        $scope.customInputs = {};
        $scope.currentOptions = {};

        var params = {"insight": $scope.selectedInsight.id};
        $http({method: "GET", url: "/cbmonitor/get_insight_options/", params: params})
        .success(function(data) {
            $scope.inputs = data;
            resetCharts();
        });
    };

    $scope.getData = function() {
        var params = {
            "insight": $scope.selectedInsight.id,
            "abscissa": $scope.abscissa,
            "inputs": JSON.stringify($scope.currentOptions)
        };
        if ($scope.vary_by !== null ) {
            params.vary_by = $scope.vary_by;
        }
        $http({method: "GET", url: "/cbmonitor/get_insight_data/", params: params})
        .success(function(data) {
            resetCharts();
            drawScatterPlot(data);
        });
    };

    $scope.updateData = function(title, value, option) {
        if (value === "Use as abscissa") {
            if ($scope.abscissa !== null && $scope.abscissa !== title) {
                $scope.currentOptions[$scope.abscissa] = $scope.resetAbscissaTo;
            }
            $scope.abscissa = title;
            $scope.resetAbscissaTo = $scope.inputs[option.$index].options[0];
        } else if ($scope.abscissa === title) {
            $scope.abscissa = null;
        }

        if (value === "Vary by") {
            if ($scope.vary_by !== null && $scope.vary_by !== title) {
                $scope.currentOptions[$scope.vary_by] = $scope.resetVaryByTo;
            }
            $scope.vary_by = title;
            $scope.resetVaryByTo = $scope.inputs[option.$index].options[0];
        } else if ($scope.vary_by === title) {
            $scope.vary_by = null;
        }

        if ($scope.abscissa !== null) {
            $scope.getData();
        } else {
            resetCharts();
        }
    };

    $http.get("/cbmonitor/get_insight_defaults/").success(function(insights) {
        $scope.insights = insights;
        $scope.selectedInsight = insights[0];
        $scope.getOptions();
    });
}


function drawBase() {
    "use strict";

    d3.select("#chart").append("svg").attr({
        height: INSIGHT.height, width: INSIGHT.width
    });

    d3.select("svg").append("rect").attr({
        height: INSIGHT.height, width: INSIGHT.width,
        rx: 5, ry: 5,
        fill: "white",
        stroke: "#cccccc"
    });
}


function drawDataPoints(circles, xScale, yScale, seqid) {
    "use strict";

    circles
        .append("circle")
        .on("mouseover", function() {
            d3.select(this).transition().duration(200)
                .attr({ r: 7 });
        })
        .on("mouseout", function() {
            d3.select(this).transition().duration(200)
                .attr({ r: 5 });
        })
        .transition().duration(500).ease("linear").each("start", function() {
            d3.select(this).attr({ fill: "white", stroke: "white" });
        })
        .attr({
            cx: function(d) { return xScale(d[0]); },
            cy: function(d) { return yScale(d[1]); },
            r: 5,
            stroke: INSIGHT.palette[seqid], "stroke-width": 3
        });
}

function drawSplines(data, xScale, yScale, seqid) {
    "use strict";

    var line = d3.svg.line()
        .x(function(d) { return xScale(d[0]); })
        .y(function(d) { return yScale(d[1]); })
        .interpolate("cardinal");

    d3.select("svg")
        .append("path")
        .attr({
            "d": line(data),
            stroke: INSIGHT.palette[seqid], "stroke-width": 2,
            "fill-opacity": 0.0
        });
}

function drawLines(lines, xScale, yScale) {
    "use strict";

    lines.append("line")
        .transition().duration(500).ease("linear").each("start", function() {
            d3.select(this).attr({ stroke: "white" });
        })
        .attr({
            x1: function(d) { return xScale(d[0]); },
            y1: function(d) { return yScale(d[1]); },
            x2: function(d) { return xScale(d[2]); },
            y2: function(d) { return yScale(d[3]); },
            stroke: "#cccccc", "shape-rendering": "crispEdges"
        });
}


function drawAxes(xScale, yScale, xTickValues) {
    "use strict";

    var smallPadding = 40,
        largePadding = 70,
        areaPadding = 10;

    var xAxis = d3.svg.axis()
                      .scale(xScale)
                      .orient("bottom")
                      .tickValues(xTickValues);

    d3.select("svg").append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0, " + (INSIGHT.height - smallPadding + areaPadding) + ")")
        .call(xAxis);

    var yAxis = d3.svg.axis()
                      .scale(yScale)
                      .orient("left")
                      .ticks(5);
    d3.select("svg").append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + (largePadding - areaPadding) + ", 0)")
        .call(yAxis);
}


function resetCharts() {
    "use strict";

    d3.selectAll("circle").remove();
    d3.selectAll("line").remove();
    d3.selectAll("g").remove();
    d3.selectAll("path").remove();
}


function drawScatterPlot(data) {
    "use strict";

    /******************************** MIN MAX *********************************/
    var xMin = Number.MAX_VALUE,
        xMax = Number.MIN_VALUE,
        yMax = Number.MIN_VALUE;

    Object.keys(data).forEach(function(key) {
        xMin = Math.min(xMin, d3.min(data[key], function(d) { return d[0]; }));
        xMax = Math.max(xMax, d3.max(data[key], function(d) { return d[0]; }));
        yMax = Math.max(yMax, d3.max(data[key], function(d) { return d[1]; }));

    });
    /********************************* SCALES *********************************/
    var smallPadding = 40,
        largePadding = 70;
    var yScale = d3.scale.linear()
                         .domain([0, yMax])
                         .range([INSIGHT.height - smallPadding, smallPadding]);
    var xScale = d3.scale.linear()
                         .domain([xMin, xMax])
                         .range([largePadding, INSIGHT.width - smallPadding]);
    /********************************** TICKS *********************************/
    var yTickValues = yScale.ticks(5);
    var xTickValues = [];
    Object.keys(data).forEach(function(key) {
        for (var i=0, l=data[key].length; i < l; i++) {
            if (xTickValues.indexOf(data[key][i][0] === -1)) {
                xTickValues.push(data[key][i][0]);
            }
        }
    });
    /********************************** GRID **********************************/
    var linesXY = [[xMax, yMax, xMin, yMax]];
    for (var i=0, l=xTickValues.length; i<l; i++) {
        linesXY.push([xTickValues[i], 0, xTickValues[i], yMax]);
    }
    for (i=0, l=yTickValues.length; i<l; i++) {
        linesXY.push([xMin, yTickValues[i], xMax, yTickValues[i]]);
    }
    var lines = d3.select("svg").selectAll("line")
                                .data(linesXY)
                                .enter();
    drawLines(lines, xScale, yScale);
    /****************************** DATA POINTS *******************************/
    var seqid = 0;
    var circles = d3.select("svg").selectAll("circle");
    Object.keys(data).forEach(function(key) {
        drawSplines(data[key], xScale, yScale, seqid);
        drawDataPoints(circles.data(data[key]).enter(), xScale, yScale, seqid);
        seqid++;
    });
    /********************************** AXES **********************************/
    drawAxes(xScale, yScale, xTickValues);
    /**************************************************************************/
}


$(document).ready(function(){
    "use strict";

    drawBase();
});
