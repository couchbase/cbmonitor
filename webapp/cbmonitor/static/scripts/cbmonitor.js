/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

/*
 * Tabs with clusters/metrics/events
 */
CBMONITOR.configureAccordion = function() {
    "use strict";

    $("#accordion").accordion({
        heightStyle: "fill"
    });
};

/*
 * Panel with buttons related to cluster management
 */
CBMONITOR.configureCPanel = function() {
    "use strict";

    $("input:button")
        .button()
        .css({
            fontSize: "77%",
            width: "23%"
        })
        .click(function() {
            switch(this.value) {
                case "Add cluster":
                    $("#dialog_new_cluster").dialog("open");
                    break;
                case "Add server":
                    $("#dialog_new_server").dialog("open");
                    break;
                case "Add bucket":
                    $("#dialog_new_bucket").dialog("open");
                    break;
                case "Edit":
                    //var selected_id = jstree.jstree("get_selected").attr("id");
                    //jstree.jstree("rename", selected_id);
                    break;
                case "Delete":
                    $("#dialog_delete").dialog("open");
                    break;
                default:
                    break;
            }
        });

    $("input:text")
        .button()
        .css({
            fontSize: "77%",
            textAlign: "left",
            cursor : "text"
        });
};

/*
 * Cluster tree
 */
CBMONITOR.configureCTree = function() {
    "use strict";

    var jstree = $("#tree"),
        renc = $("#renc"),
        delc = $("#delc"),
        adds = $("#adds");

    // Disable buttons
    renc.addClass("ui-state-disabled");
    delc.addClass("ui-state-disabled");
    adds.addClass("ui-state-disabled");

    // Create tree
    jstree.jstree({
        "themes" : {
            "theme" : "default",
            "icons" : false
        },
        "crrm": {
            "move": {
                "check_move": function (m) {
                    var p = this._get_parent(m.o);
                    if (!p) {
                        return false;
                    }
                    p = p === -1 ? this.get_container() : p;
                    if (p === m.np) {
                        return true;
                    }
                    return p[0] && m.np[0] && p[0] === m.np[0];
                }
            }
        },
        "dnd": {
            "drop_target": false,
            "drag_target": false
        },
        "plugins": ["themes", "json_data", "dnd", "ui", "crrm"],
        "json_data": {
            "ajax" : {
                "url" : "/cbmonitor/get_tree_data/"
            }
        }
    });

    // Expand all nodes
    jstree.on("loaded.jstree", function() {
        jstree.jstree("open_all");
    });

    // Define binding
    jstree.bind("select_node.jstree", function (event, data) {
        var cls = data.rslt.obj.attr("class").split(" ")[0];
        switch(cls) {
            case "cluster":
                //renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add server");
                break;
            case "server":
                //renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add bucket");
                break;
            case "bucket":
                //renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.addClass("ui-state-disabled");
                break;
            default:
                break;
        }
    });
};

/*
 * Panel with radio buttons related to chart views
 */
CBMONITOR.configureChartPanel = function() {
    "use strict";

    $("#vpanel").buttonset();
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
    });
    $("#rpanel").buttonset();
};

CBMONITOR.configureMEPanel = function() {
    "use strict";

    CBMONITOR.configureClusters($("#met_cluster"), $("#met_server"), $("#met_bucket"));
    CBMONITOR.configureClusters($("#evnt_cluster"), $("#evnt_server"), $("#evnt_bucket"));
};

CBMONITOR.configureClusters = function(c_sel, s_sel, b_sel) {
    "use strict";

    $.ajax({url: "/cbmonitor/get_clusters/", dataType: "json",
        success: function(clusters){
            c_sel.empty();
            clusters.forEach(function(cluster) {
                var o = new Option(cluster, cluster);
                c_sel.append(o);
            });
            c_sel.selectmenu({
                select: function(event, option) {
                    CBMONITOR.configureMEServers(option.value, s_sel, b_sel);
                }
            });
            CBMONITOR.configureMEServers(clusters[0], s_sel, b_sel);
        }
    });
};

CBMONITOR.configureMEServers = function(cluster, s_sel, b_sel) {
    "use strict";

    $.ajax({url: "/cbmonitor/get_servers/", dataType: "json",
        data: {"cluster": cluster},
        success: function(servers) {
            s_sel.empty();
            var o = new Option("None", null);
            s_sel.append(o);
            servers.forEach(function(server) {
                var o = new Option(server, server);
                s_sel.append(o);
            });
            s_sel.selectmenu({
                select: function(event, option) {
                    CBMONITOR.configureMEBuckets(option.value, b_sel);
                }
            });
            CBMONITOR.configureMEBuckets(servers[0], b_sel);
        }
    });
};

CBMONITOR.configureMEBuckets = function(server, b_sel) {
    "use strict";

    console.log(server);


    $.ajax({url: "/cbmonitor/get_buckets/", dataType: "json",
        data: {"server": server},
        success: function(buckets){
            b_sel.empty();
            var o = new Option("None", null);
            b_sel.append(o);
            buckets.forEach(function(bucket) {
                var o = new Option(bucket, bucket);
                b_sel.append(o);
            });
            b_sel.selectmenu();
        }
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.configureMEPanel();
    CBMONITOR.configureAccordion();
    CBMONITOR.configureCPanel();
    CBMONITOR.configureCTree();
    CBMONITOR.addNewCluster();
    CBMONITOR.addNewServer();
    CBMONITOR.addNewBucket();
    CBMONITOR.deleteItem();
    CBMONITOR.configureChartPanel();
});