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

    return new Spinner({
        lines: 10,
        length: 10,
        width: 6,
        radius: 15,
        corners: 1,
        color: "#777",
        top: 20
    }).spin(document.getElementById("spinner"));
}

function Comparison($scope, $http) {
    "use strict";

    $scope.filter = function(userInput, baseline) {
        var filtered = null;
        for (var i = 0, l = $scope.snapshots.length; i < l; i++) {
            if ($scope.snapshots[i].indexOf(userInput) !== -1) {
                filtered = $scope.snapshots[i];
                break;
            }
        }
        if (filtered !== null) {
            $("#compare").attr("disabled", false);
            if (baseline) {
                $scope.selectedBaseline = filtered;
            } else {
                $scope.selectedTarget = filtered;
            }
        } else {
            $("#compare").attr("disabled", true);
        }
    };

    $scope.compareSnapshots = function() {
        $scope.diffs = [];
        $scope.error = null;
        $scope.info = null;
        $scope.url = null;

        var spinner = startSpinner();

        var url = '/reports/html/?snapshot=' + $scope.selectedBaseline +
            '&snapshot=' + $scope.selectedTarget;

        $http.get(url)
            .success(function() {
                $scope.url = url;

                var params = {
                    baseline: $scope.selectedBaseline,
                    target: $scope.selectedTarget
                };

                $http({method: 'GET', url: '/reports/compare/', params: params})
                    .success(function(data) {
                        spinner.stop();
                        for (var i = 0, l = data.length; i < l; i++) {
                            if (data[i][1] > 50 && $scope.diffs.indexOf(data[i][0]) === -1) {
                                $scope.diffs.push(data[i][0]);
                            }
                        }
                        if ($scope.diffs.length === 0) {
                            $scope.info = "No difference";
                        }
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
            })
            .error(function() {
                spinner.stop();
                $scope.error = "Something went wrong";
            });
    };

    $scope.url = null;
    $scope.error = null;
    $scope.info = null;
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
