/*jshint jquery: true, browser: true*/
/*global angular*/

angular.module('insight', [])
    .config(['$interpolateProvider', function ($interpolateProvider) {
        "use strict";

        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }]);


function getOptions($scope, $http, insight) {
    "use strict";

    var params = {"insight": insight};
    $scope.inputs = [];

    $http({method: 'GET', url: '/cbmonitor/get_insight_options/', params: params})
    .success(function(data) {
        $scope.inputs = data;
    });
}


function Insights($scope, $http) {
    "use strict";

    $http.get('/cbmonitor/get_insight_defaults/').success(function(insights) {
        $scope.insights = insights;
        getOptions($scope, $http, insights[0].id);
    });
}
