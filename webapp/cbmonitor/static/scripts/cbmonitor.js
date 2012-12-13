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

    var jstree = $("#tree"),
        renc = $("#renc"),
        delc = $("#delc"),
        adds = $("#adds");

    $("input:button")
        .button()
        .css({
            fontSize: "77%",
            width: "23%"
        })
        .click(function() {
            var selected = jstree.jstree("get_selected"),
                selected_id = selected.attr("id");
            switch(this.value) {
                case "Add cluster":
                    jstree.jstree("create", -1, "last", {"attr": {"class": "cluster"}});
                    break;
                case "Add server":
                    jstree.jstree("create", null, "last", {"attr": {"class": "server"}});
                    break;
                case "Add bucket":
                    jstree.jstree("create", null, "last", {"attr": {"class": "bucket"}});
                    break;
                case "Edit":
                    jstree.jstree("rename", selected_id);
                    break;
                case "Delete":
                    var prnt = $.jstree._reference(selected)._get_parent(selected),
                        prev = $.jstree._reference(selected)._get_prev(selected);
                    if (prnt === -1 && prev === false) {
                        renc.addClass("ui-state-disabled");
                        delc.addClass("ui-state-disabled");
                        adds.addClass("ui-state-disabled");
                    }
                    jstree.jstree("remove", selected_id);
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
        "json_data": {"data": []}
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
                renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add server");
                break;
            case "server":
                renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.removeClass("ui-state-disabled");
                adds.prop("value", "Add bucket");
                break;
            case "bucket":
                renc.removeClass("ui-state-disabled");
                delc.removeClass("ui-state-disabled");
                adds.addClass("ui-state-disabled");
                break;
            default:
                break;
        }
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.configureAccordion();
    CBMONITOR.configureCPanel();
    CBMONITOR.configureCTree();
});