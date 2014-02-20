/*jshint jquery: true, browser: true*/
/*global angular, d3, Spinner*/

angular.module("comparison", [])
    .config(["$interpolateProvider", function ($interpolateProvider) {
        "use strict";

        $interpolateProvider.startSymbol("[[");
        $interpolateProvider.endSymbol("]]");
    }]);


function startSpinner() {
    "use strict";

    var spinner = new Spinner({
        lines: 10,
        length: 10,
        width: 6,
        radius: 15,
        corners: 1,
        color: "#777",
        top: 20
    }).spin(document.getElementById("spinner"));

    return spinner;
}

function Comparison($scope, $http) {
    "use strict";

    $scope.compareSnapshots = function() {
        var params = {
            baseline: $scope.selectedBaseline,
            target: $scope.selectedTarget
        };
        $scope.diffs = [];
        var maxSize = screen.availHeight * 0.95;
        var spinner = startSpinner(maxSize);

        $http({method: 'GET', url: '/reports/compare/', params: params})
            .success(function(data) {
                for (var i = 0, l = data.length; i < l; i++) {
                    if (data[i][1] > 50) {
                        $scope.diffs.push(data[i][0]);
                    }
                }
                spinner.stop();
                $scope.diffs = data;
                $scope.error = null;

            })
            .error(function(err, code) {
                spinner.stop();
                if (code === 400) {
                    $scope.error = err;
                }
                else {
                    $scope.error = "Something went wrong";
                }
            });
    };

    $scope.error = null;
    $scope.diffs = [];

    $http.get("/cbmonitor/get_all_snapshots/").success(function(snapshots) {
        $scope.snapshots = snapshots;
        $scope.selectedBaseline = snapshots[0];
        $scope.selectedTarget = snapshots[0];
        });
}


$(document).ready(function(){
    "use strict";

    $(".diffs").css("margin-left", (screen.width / 2 - 300) + "px");
});
