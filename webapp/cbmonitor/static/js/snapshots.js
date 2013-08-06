/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};


CBMONITOR.Snapshots = function () {
    "use strict";

    $("#add").click(function() {
        $("#add_new_snapshot").dialog("open");
    });

    $("#html").click(function() {
        var data = {
            snapshot: $("#snapshot").find(":selected").text(),
            cluster: $("#met_cluster").find(":selected").text(),
            report: $("#report").find(":selected").text()
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

CBMONITOR.Snapshots.prototype.getReportTypes = function () {
    "use strict";

    $.ajax({url: "/cbmonitor/get_report_types/", dataType: "json",
        success: function(types){
            types.forEach(function(type) {
                var o = new Option(type, type);
                $("#report").append(o);
            });
        }
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
    CBMONITOR.snapshots.getReportTypes();

    CBMONITOR.dialogs = new CBMONITOR.Dialogs();
    CBMONITOR.dialogs.configureAddNewSnapshot();
});