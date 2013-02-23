/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.Observables = function () {};

CBMONITOR.Observables.prototype.updateSelectors = function() {
    "use strict";

    this.updateClusters("metric");
    this.updateClusters("event");
};

CBMONITOR.Observables.prototype.updateClusters = function(type) {
    "use strict";

    var that = this;
    $.ajax({url: "/cbmonitor/get_clusters/", dataType: "json",
        success: function(clusters){
            var sel = (type === "metric") ? $("#met_cluster") : $("#evnt_cluster");
            sel.empty();
            if (!clusters.length) {
                var o = new Option("None", "");
                sel.append(o);
            }
            clusters.forEach(function(cluster) {
                var o = new Option(cluster, cluster);
                sel.append(o);
            });
            sel.change(function() {
                var cluster = sel.find(":selected").text();
                that.updateItems(cluster, type, "server");
                that.updateItems(cluster, type, "bucket");
            });
            that.updateItems(clusters[0], type, "server");
            that.updateItems(clusters[0], type, "bucket");
        }
    });
};

CBMONITOR.Observables.prototype.updateItems = function(cluster, type, item) {
    "use strict";

    var that = this;
    $.ajax({url: "/cbmonitor/get_" + item + "s/", dataType: "json",
        data: {"cluster": cluster},
        success: function(items) {
            var sel = (type === "metric") ? $("#met_" + item) : $("#evnt_" + item);
            sel.empty();
            var o = new Option("None", "");
            sel.append(o);
            items.forEach(function(item) {
                var o = new Option(item, item);
                sel.append(o);
            });
            sel.change(function() {
                that.getMetricsAndEvents(type);
            });
            that.getMetricsAndEvents(type);
        }
    });
};

CBMONITOR.Observables.prototype.getMetricsAndEvents = function(type) {
    "use strict";

    var prefix = (type === "metric")? "met" : "evnt",
        cluster = $("#" + prefix + "_cluster option:selected").val(),
        server = $("#" + prefix + "_server option:selected").val(),
        bucket = $("#" + prefix + "_bucket option:selected").val();
    $.ajax({
        url: "/cbmonitor/get_metrics_and_events/", dataType: "json",
        data: {
            "cluster": cluster,
            "server": server,
            "bucket": bucket,
            "type": type
        },
        success: function(items) {
            var ul = (type === "metric") ? "#metrics_ul" : "#events_ul";
            $(ul).empty();
            items.forEach(function(item) {
                $(ul).append(
                    $("<li>").addClass("ui-state-default ui-corner-all")
                        .attr("type", type)
                        .attr("cluster", cluster)
                        .attr("server", server)
                        .attr("bucket", bucket)
                        .append(item)
                );
            });
            $(ul + " li").draggable({
                "revert": "invalid",
                "appendTo": "#views",
                "helper": "clone",
                "cursor": "move"
            });
        }
    });
};