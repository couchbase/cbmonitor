/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.Inventory = function () {};

/*
 * Panel with buttons related to cluster management
 */
CBMONITOR.Inventory.prototype.configureButtons = function() {
    "use strict";

    $(".inventorybtn:button")
        .css({
            fontSize: "77%"
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
};

/*
 * Inventory tree
 */
CBMONITOR.Inventory.prototype.configureTree = function() {
    "use strict";

    var jstree = $("#tree"),
        renc = $("#renc"),
        delc = $("#delc"),
        adds = $("#adds");

    // Disable buttons
    renc.addClass("ui-state-disabled");
    delc.addClass("ui-state-disabled");
    adds.addClass("ui-state-disabled");

    // Cleanup (bootstrap bug)
    jstree.remove();
    $("<div/>", {id: "tree"}).appendTo('#inventory');
    jstree = $("#tree");

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
                delc.removeClass("ui-state-disabled");
                adds.addClass("ui-state-disabled");
                CBMONITOR.inventory.getCollectors(data.rslt.obj.attr("id"));
                break;
            case "servers":
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add server");
                adds.prop("innerHTML", "Add server");
                break;
            case "server":
                delc.removeClass("ui-state-disabled");
                adds.addClass("ui-state-disabled");
                break;
            case "buckets":
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add bucket");
                adds.prop("innerHTML", "Add bucket");
                break;
            case "bucket":
                delc.removeClass("ui-state-disabled");
                adds.addClass("ui-state-disabled");
                break;
            default:
                break;
        }
    });
};


/*
 * Display cluster collectors
 */
CBMONITOR.Inventory.prototype.getCollectors = function(cluster) {
    "use strict";

    CBMONITOR.inventory.cnames = [];

    $.ajax({url: "/cbmonitor/get_collectors/", dataType: "json",
        data: {"cluster": cluster},
        success: function(collectors){
            var container = $("#collectors");
            container.empty();

            collectors.forEach(function(collector) {
                var id = collector.name.replace(/\s+/g,"_");
                CBMONITOR.inventory.cnames.push(collector.name);

                $("<div/>").attr({
                    "class": "collector",
                    id: id
                }).appendTo(container);

                $("<div/>").attr({
                    "class": "coll-name"
                }).html(collector.name).appendTo("#" + id);
                $("<div/>").attr({
                    "class": "coll-interval",
                    "id": "interval" + id
                }).appendTo("#" + id);
                $("<div/>").attr({
                    "class": "coll-enabled",
                    "id": "enabled" + id
                }).appendTo("#" + id);

                $("</br>").appendTo(container);

                $("<input>").attr({
                    id: "checkbox" + id,
                    type: "checkbox",
                    checked: collector.enabled
                }).appendTo("#enabled" + id);

                $("<input>").attr({
                    "id": "spinner" + id,
                    "class": "spinner",
                    "value": collector.interval
                }).appendTo("#interval" + id);

                $("#spinner" + id).spinner({min: 1});
            });

            $("#apply").css("display", "block");
        }
    });
};

CBMONITOR.Inventory.prototype.bindApplySettings = function() {
    "use strict";

    $("#apply").bind("click", function() {
        CBMONITOR.inventory.cnames.forEach(function(cname) {
            var id = cname.replace(/\s+/g,"_");
            var collector = {
                "cluster": $("#tree").jstree('get_selected').attr('id'),
                "name": cname,
                "interval": $("#spinner" + id).val(),
                "enabled": $("#checkbox" + id).is(":checked")
            };
            $.ajax({url: "/cbmonitor/update_collectors/", method: "POST",
                    dataType: "json", data: collector});
        });
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.inventory = new CBMONITOR.Inventory();
    CBMONITOR.inventory.configureButtons();
    CBMONITOR.inventory.configureTree();
    CBMONITOR.inventory.bindApplySettings();

    CBMONITOR.dialogs = new CBMONITOR.Dialogs();
    CBMONITOR.dialogs.configureAddNewCluster();
    CBMONITOR.dialogs.configureAddNewServer();
    CBMONITOR.dialogs.configureAddNewBucket();
    CBMONITOR.dialogs.configureDeleteItem();

});