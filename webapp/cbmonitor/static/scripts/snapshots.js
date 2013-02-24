/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};


CBMONITOR.Snapshots = function () {};

CBMONITOR.Snapshots.prototype.getClusters = function () {
    "use strict";

    $.ajax({url: "/cbmonitor/get_snapshots/", dataType: "json",
        success: function(snapshots){
            var sel = $("#snapshot");
            if (snapshots.length) {
                snapshots.forEach(function(snapshot) {
                    var o = new Option(snapshot, snapshot);
                    sel.append(o);
                });
            } else {
                $("#plot").addClass("disabled");
                var o = new Option("None", "");
                sel.append(o);
            }
        }
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
    CBMONITOR.snapshots.getClusters();
});