/*jshint jquery: true, browser: true*/
/*global angular*/

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
        }
    };

    $http.get("/cbmonitor/get_insight_defaults/").success(function(insights) {
        $scope.insights = insights;
        $scope.selectedInsight = insights[0];
        $scope.getOptions();
    });
}
