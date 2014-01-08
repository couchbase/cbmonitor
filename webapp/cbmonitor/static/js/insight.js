/*jshint jquery: true, browser: true*/
/*global angular, d3*/

angular.module("insight", [])
    .config(["$interpolateProvider", function ($interpolateProvider) {
        "use strict";

        $interpolateProvider.startSymbol("[[");
        $interpolateProvider.endSymbol("]]");
    }]);


function Insights($scope, $http) {
    "use strict";

    $scope.getOptions = function() {
        $scope.inputs = [];
        $scope.abscissa = null;
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
        $http({method: "GET", url: "/cbmonitor/get_insight_data/", params: params})
        .success(function(data) {
            $scope.data = data;
            resetCharts();
            drawScatterPlot(data);
        });
    };

    $scope.updateData = function(title, value, option) {
        if (value === "Use as abscissa") {
            if ($scope.abscissa !== null && $scope.abscissa !== title) {
                $scope.currentOptions[$scope.abscissa] = $scope.resetTo;
            }
            $scope.abscissa = title;
            $scope.resetTo = $scope.inputs[option.$index].options[0];
        } else if ($scope.abscissa === title) {
            $scope.abscissa = null;
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


function drawBase(height, width) {
    "use strict";

    d3.select("#chart").append("svg").attr({
        height: height, width: width
    });

    d3.select("svg").append("rect").attr({
        height: height, width: width,
        rx: 5, ry: 5,
        fill: "white",
        stroke: "#cccccc"
    });
}


function drawDataPoints(circles, xScale, yScale) {
    "use strict";

    circles
        .append("circle")
        .on("mouseover", function() {
            d3.select(this).transition().duration(200)
                .attr({ r: 8 });
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
            r: 5, stroke: "#f89406", "stroke-width": 3
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
            stroke: "#cccccc", "stroke-dasharray": "5, 5", "stroke-width": 1
        });
}


function drawAxes(xScale, yScale, xTickValues, yTickValues) {
    "use strict";

    var height = 548,
        smallPadding = 40,
        largePadding = 70,
        areaPadding = 10;

    var xAxis = d3.svg.axis()
                      .scale(xScale)
                      .orient("bottom")
                      .tickValues(xTickValues);

    d3.select("svg").append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0, " + (height - smallPadding + areaPadding) + ")")
        .call(xAxis);

    var yAxis = d3.svg.axis()
                      .scale(yScale)
                      .orient("left")
                      .tickValues(yTickValues);
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
}


function drawScatterPlot(data) {
    "use strict";

    var height = 548,
        width = 900,
        smallPadding = 40,
        largePadding = 70;

    var xMax = d3.max(data, function(d) { return d[0]; });
    var xMin = d3.min(data, function(d) { return d[0]; });
    var yMax = d3.max(data, function(d) { return d[1]; });

    var yScale = d3.scale.linear()
                         .domain([0, yMax])
                         .range([height - smallPadding, smallPadding]);
    var xScale = d3.scale.linear()
                         .domain([xMin, xMax])
                         .range([largePadding, width - smallPadding]);

    var circles = d3.select("svg").selectAll("circle")
                                  .data(data)
                                  .enter();
    drawDataPoints(circles, xScale, yScale);

    var linesXY = [[xMax, yMax, xMax, 0], [xMax, yMax, xMin, yMax]];
    var lines = d3.select("svg").selectAll("line")
                                .data(linesXY)
                                .enter();
    drawLines(lines, xScale, yScale);

    var xTickValues = [],
        yTickValues = [];
    for (var i=0, l=data.length; i < l; i++) {
        xTickValues.push(data[i][0]);
        yTickValues.push(data[i][1]);
    }
    drawAxes(xScale, yScale, xTickValues, yTickValues);
}


$(document).ready(function(){
    "use strict";

    drawBase(548, 900);
});
