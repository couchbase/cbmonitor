/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};


CBMONITOR.Snapshots = function () {};

CBMONITOR.Snapshots.prototype.getClusters = function () {
    "use strict";

    var that = this;
    $.ajax({url: "/cbmonitor/get_snapshots/", dataType: "json",
        success: function(snapshots){
            var sel = $("#snapshot");
            if (snapshots.length) {
                snapshots.forEach(function(snapshot) {
                    var o = new Option(snapshot, snapshot);
                    sel.append(o);
                });
                $("#plot").click(function() {
                    that.plot();
                });
            } else {
                $("#plot").addClass("disabled");
                var o = new Option("None", "");
                sel.append(o);
            }
        }
    });
};

CBMONITOR.Snapshots.prototype.plot = function () {
    "use strict";

    var snapshot = $("#snapshot").find(":selected").text();

    var spinner = new Spinner({width: 4, top: "150px"});
    spinner.spin(document.getElementById('spinner'));

    $.ajax({url: "/cbmonitor/plot/", dataType: "json", type: "POST",
        data: {snapshot: snapshot},
        success: function(images) {
            spinner.stop();
        },
        error: function() {
            spinner.stop();
        }
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
    CBMONITOR.snapshots.getClusters();
});