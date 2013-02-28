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

    var spinner = new Spinner({width: 4, top: "210px"});
    spinner.spin(document.getElementById('spinner'));

    $(".carousel").css("display", "none");
    var that = this;
    $.ajax({url: "/cbmonitor/plot/", dataType: "json", type: "POST",
        data: {snapshot: snapshot},
        success: function(images) {
            spinner.stop();
            if (images.length) {
                $.each(images, function(index, value) {
                    that.addLink(index, value[0]);
                    that.addIndicator(index);
                    that.addItem(index, value[1]);
                });
                $("#carousel-indicator0").addClass("active");
                $("#carousel-item0").addClass("active");
                $('.carousel').carousel({
                    interval: false
                });
                $(".carousel").css("display", "block");
            }
        },
        error: function() {
            spinner.stop();
        }
    });
};

CBMONITOR.Snapshots.prototype.addLink = function (index, title) {
    "use strict";

    $("#titles").append(
        $("<a>")
            .append(title)
            .attr("href", "#")
            .click(function() {
                $('.carousel').carousel(index);
            })
    ).append("<br>");
};

CBMONITOR.Snapshots.prototype.addIndicator = function (index) {
    "use strict";

    $(".carousel-indicators").append(
        $("<li>")
            .attr("id", "carousel-indicator" + index)
            .attr("data-target", "#carousel")
            .attr("data-slide-to", index.toString())
    );
};

CBMONITOR.Snapshots.prototype.addItem = function (index, url) {
    "use strict";

    $(".carousel-inner").append(
        $("<div>")
            .addClass("item")
            .attr("id", "carousel-item" + index)
            .append($("<img>").attr("src", url))
    );
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
    CBMONITOR.snapshots.getClusters();
});