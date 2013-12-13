/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.Observables = function () {};

CBMONITOR.Observables.prototype.updateSelectors = function() {
    "use strict";

    this.updateClusters();
};

CBMONITOR.Observables.prototype.updateClusters = function() {
    "use strict";

    var that = this;
    $.ajax({url: "/cbmonitor/get_clusters/", dataType: "json",
        success: function(clusters){
            var sel = $("#met_cluster");
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
                that.updateItems(cluster, "server");
                that.updateItems(cluster, "bucket");
                that.getSnapshots(cluster);
            });
            that.updateItems(clusters[0], "server");
            that.updateItems(clusters[0], "bucket");
            that.getSnapshots(clusters[0]);
        }
    });
};

CBMONITOR.Observables.prototype.updateItems = function(cluster, item) {
    "use strict";

    var that = this;
    $.ajax({url: "/cbmonitor/get_" + item + "s/", dataType: "json",
        data: {"cluster": cluster},
        success: function(items) {
            var sel = $("#met_" + item);
            sel.empty();
            var o = new Option("None", "");
            sel.append(o);
            items.forEach(function(item) {
                var o = new Option(item, item);
                sel.append(o);
            });
            sel.change(function() {
                that.getMetrics();
            });
            that.getMetrics();
        }
    });
};

CBMONITOR.Observables.prototype.getMetrics = function() {
    "use strict";

    var cluster = $("#met_cluster option:selected").val(),
        server = $("#met_server option:selected").val(),
        bucket = $("#met_bucket option:selected").val();
    $.ajax({
        url: "/cbmonitor/get_metrics/", dataType: "json",
        data: {
            "cluster": cluster,
            "server": server,
            "bucket": bucket
        },
        success: function(items) {
            var ul = "#metrics_ul";
            $(ul).empty();
            items.forEach(function(item) {
                $(ul).append(
                    $("<li>").addClass("ui-state-default ui-corner-all")
                        .attr("cluster", cluster)
                        .attr("server", server)
                        .attr("bucket", bucket)
                        .attr("collector", item.collector)
                        .append(item.name)
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

CBMONITOR.Observables.prototype.getSnapshots = function (cluster) {
    "use strict";

    $.ajax({url: "/cbmonitor/get_snapshots/", dataType: "json",
        data: {"cluster": cluster},
        success: function(snapshots){
            var sel = $("#snapshot");
            sel.empty();
            snapshots.forEach(function(snapshot) {
                var o = new Option(snapshot, snapshot);
                sel.append(o);
            });
        }
    });
};