/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.addNewCluster = function() {
    "use strict";

    var jstree = $("#tree"),
        name = $("#name"),
        description = $("#description");

    $("#dialog_new_cluster").dialog({
        autoOpen: false,
        height: 330,
        width: 350,
        modal: true,
        resizable: false,
        buttons: {
            "Add new cluster": function() {
                $.ajax({
                    type: "POST", url: "/cbmonitor/add_cluster/",
                    data: {
                        "name": name.val(),
                        "description": description.val()
                    },
                    success: function(){
                        jstree.jstree("create", -1, "last",
                            {
                                "attr": {"class": "cluster", "id": name.val()},
                                "data": name.val()
                            },
                            false, true
                        );
                    }
                });
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

    var jstree = $("#tree"),
        address = $("#address"),
        rest_username = $("#rest_username"),
        rest_password = $("#rest_password"),
        ssh_username = $("#ssh_username"),
        ssh_password = $("#ssh_password"),
        ssh_key = $("#ssh_key"),
        description = $("#description");

    $("#dialog_new_server").dialog({
        autoOpen: false,
        resizable: false,
        height: 620,
        width: 400,
        modal: true,
        buttons: {
            "Add new server": function() {
                $.ajax({
                    type: "POST", url: "/cbmonitor/add_server/",
                    data: {
                        "address": address.val(),
                        "cluster": jstree.jstree("get_selected").attr("id"),
                        "rest_username": rest_username.val(),
                        "rest_password": rest_password.val(),
                        "ssh_username": ssh_username.val(),
                        "ssh_password": ssh_password.val(),
                        "ssh_key": ssh_key.val(),
                        "description": description.val()
                    },
                    success: function(){
                        jstree.jstree("create", null, "last",
                            {
                                "attr": {"class": "server", "id": address.val()},
                                "data": address.val()
                            },
                            false, true
                        );
                    }
                });
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

    var jstree = $("#tree"),
        name = $("#name"),
        type = $("#type"),
        port = $("#port"),
        password = $("#password");

    $("#dialog_new_bucket").dialog({
        autoOpen: false,
        resizable: false,
        height: 410,
        width: 350,
        modal: true,
        buttons: {
            "Add new bucket": function() {
                $.ajax({
                    type: "POST", url: "/cbmonitor/add_bucket/",
                    data: {
                        "name": name.val(),
                        "server": jstree.jstree("get_selected").attr("id"),
                        "type": type.val(),
                        "port": port.val(),
                        "password": password.val()
                    },
                    success: function(){
                        jstree.jstree("create", null, "last",
                            {
                                "attr": {"class": "bucket", "id": name.val()},
                                "data": name.val()
                            },
                            false, true
                        );
                    }
                });
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
                    selected_class = selected.attr("class").split(" ")[0],
                    renc = $("#renc"),
                    delc = $("#delc"),
                    adds = $("#adds"),
                    prnt = $.jstree._reference(selected)._get_parent(selected),
                    prev = $.jstree._reference(selected)._get_prev(selected),
                    data,
                    url;

                switch(selected_class) {
                    case "cluster":
                        data = {"name": selected_id};
                        url = "/cbmonitor/delete_cluster/";
                        break;
                    case "server":
                        data = {"address": selected_id};
                        url = "/cbmonitor/delete_server/";
                        break;
                    case "bucket":
                        data = {"name": selected_id, "server": prnt.attr("id")};
                        url = "/cbmonitor/delete_bucket/";
                        break;
                    default:
                        break;
                }
                $.ajax({
                    type: "POST", url: url, data: data,
                    success: function(){
                        if (prnt === -1 && prev === false) {
                            renc.addClass("ui-state-disabled");
                            delc.addClass("ui-state-disabled");
                            adds.addClass("ui-state-disabled");
                        }
                        jstree.jstree("remove", selected);
                    }
                });
                $(this).dialog("close");
            },
            Cancel: function() {
                $(this).dialog("close");
            }
        }
    });
};