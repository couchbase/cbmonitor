/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

/*
 * Modal dialogs for adding/removing clusters, servers, buckets
 */
CBMONITOR.Views = function () {};

/*
 * Panel with radio buttons related to chart views
 */
CBMONITOR.Views.prototype.configurePanel = function() {
    "use strict";

    var that = this;
    $(".vradio").click(function() {
        var views = $("#views");
        views.empty();
        switch(this.id) {
            case "view1":
                $("<div/>", {
                    "id": "first_view",
                    "class": "chart_view_single"
                }).appendTo(views);
                break;
            case "view2":
                $("<div/>", {
                    "id": "first_view",
                    "class": "chart_view_double"
                }).appendTo(views);
                $("<div/>", {
                    "id": "second_view_double",
                    "class": "chart_view_double"
                }).appendTo(views);
                break;
            case "view4":
                $("<div/>", {
                    "id": "first_view",
                    "class": "chart_view_quadruple"
                }).appendTo(views);
                $("<div/>", {
                    "id": "second_view",
                    "class": "chart_view_quadruple"
                }).appendTo(views);
                $("<div/>", {
                    "id": "third_view",
                    "class": "chart_view_quadruple"
                }).appendTo(views);
                $("<div/>", {
                    "id": "fourth_view",
                    "class": "chart_view_quadruple"
                }).appendTo(views);
                break;
            default:
                break;
        }
        CBMONITOR.graphManager.clear();
        that.enableDroppable();
    });
    $("#view1").button("toggle");

    $("#clear_views")
        .click(function() {
            CBMONITOR.graphManager.clear();
        });

    if ($.cookie("ZoomEnabled") === undefined) {
        $.cookie("ZoomEnabled", true, {expires: 60});
    }

    if ($.cookie("Lines") === undefined) {
        $.cookie("Lines", true, {expires: 60});
    }

    if ($.cookie("Lines") !== "true") {
        $("#views").toggleClass("dotted");
    }

    $("#zoom")
        .attr("checked", $.cookie("ZoomEnabled") === "true")
        .click(function() {
            CBMONITOR.graphManager.clear();
            $.cookie("ZoomEnabled", $.cookie("ZoomEnabled") !== "true", {expires: 60});
        });

    $("#lines")
        .attr("checked", $.cookie("Lines") === "true")
        .click(function() {
            $("#views").toggleClass("dotted");
            $.cookie("Lines", $.cookie("Lines") !== "true", {expires: 60});
        });

    $("#all").button("toggle");
};

CBMONITOR.Views.prototype.enableDroppable = function() {
    "use strict";

    $("#views div").droppable({
        activeClass: "ui-state-default",
        hoverClass: "ui-state-hover",
        drop: function(event, ui) {
            if ($("#zoom").prop('checked')) {
                CBMONITOR.graphManager.plot($(this).attr("id"), ui, "lineWithFocus");
            } else {
                CBMONITOR.graphManager.plot($(this).attr("id"), ui);
            }
        }
    });
};
