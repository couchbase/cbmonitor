/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};


CBMONITOR.Snapshots = function () {
    "use strict";

    $("#html").click(function() {
        var data = {
            snapshot: $("#snapshot").find(":selected").text(),
            cluster: $("#met_cluster").find(":selected").text()
        };
        var params = [];
        for (var param in data) {
            if (data.hasOwnProperty(param)) {
                params.push(
                    encodeURIComponent(param) + "=" + encodeURIComponent(data[param])
                );
            }
        }
        window.open("/reports/html/?" + params.join("&"), '_blank');
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
});