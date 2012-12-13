/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.addNewCluster = function() {
    "use strict";

    var name = $("#name"),
        jstree = $("#tree");

    $("#dialog_new_cluster").dialog({
        autoOpen: false,
        height: 330,
        width: 350,
        modal: true,
        resizable: false,
        buttons: {
            "Add new cluster": function() {
                jstree.jstree("create", -1, "last",
                    {
                        "attr": {"class": "cluster"},
                        "data": name.val()
                    },
                    false, true
                );
                $(this).dialog("close");
            },
            Cancel: function() {
                $(this).dialog("close");
            }
        }
    });
};

CBMONITOR.addNewServer = function() {
    "use strict";

    var address = $("#address"),
        jstree = $("#tree");

    $("#dialog_new_server").dialog({
        autoOpen: false,
        resizable: false,
        height: 620,
        width: 400,
        modal: true,
        buttons: {
            "Add new server": function() {
                jstree.jstree("create", null, "last",
                    {
                        "attr": {"class": "server"},
                        "data": address.val()
                    },
                    false, true
                );
                $(this).dialog("close");
            },
            Cancel: function() {
                $(this).dialog("close");
            }
        }
    });
};

CBMONITOR.addNewBucket = function() {
    "use strict";

    var name = $("#name"),
        jstree = $("#tree");

    $("#dialog_new_bucket").dialog({
        autoOpen: false,
        resizable: false,
        height: 410,
        width: 350,
        modal: true,
        buttons: {
            "Add new bucket": function() {
                jstree.jstree("create", null, "last",
                    {
                        "attr": {"class": "bucket"},
                        "data": name.val()
                    },
                    false, true
                );
                $(this).dialog("close");
            },
            Cancel: function() {
                $(this).dialog("close");
            }
        }
    });
};

CBMONITOR.deleteItem = function() {
    "use strict";

    $("#dialog_delete").dialog({
        autoOpen: false,
        resizable: false,
        height:160,
        modal: true,
        buttons: {
            "Delete": function() {
                var jstree = $("#tree"),
                    selected = jstree.jstree("get_selected"),
                    selected_id = selected.attr("id"),
                    renc = $("#renc"),
                    delc = $("#delc"),
                    adds = $("#adds"),
                    prnt = $.jstree._reference(selected)._get_parent(selected),
                    prev = $.jstree._reference(selected)._get_prev(selected);

                if (prnt === -1 && prev === false) {
                    renc.addClass("ui-state-disabled");
                    delc.addClass("ui-state-disabled");
                    adds.addClass("ui-state-disabled");
                }
                jstree.jstree("remove", selected_id);
                $(this).dialog("close");
            },
            Cancel: function() {
                $(this).dialog("close");
            }
        }
    });
};