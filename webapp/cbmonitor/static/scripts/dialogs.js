/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.highlightErrors = function(jqXHR, prefix) {
    "use strict";

    var response = JSON.parse(jqXHR.responseText),
        $key;
    for (var key in response) {
        if (response.hasOwnProperty(key)) {
            if (key === "name") {
                $key = $("#" + prefix + key);
            } else if (key === "__all__") {
                $key = $("#ssh_password");
                $key.addClass("ui-state-error");
                $key = $("#ssh_key");
            } else {
                $key = $("#" + key);
            }
            $key.addClass("ui-state-error");
        }
    }
};

CBMONITOR.getSelectedParent = function(selected) {
    "use strict";

    if (selected === undefined) {
        selected = $("#tree").jstree("get_selected");
    }
    return $.jstree._reference(selected)._get_parent(selected);
};

CBMONITOR.addNewCluster = function() {
    "use strict";

    var jstree = $("#tree"),
        name = $("#cname"),
        description = $("#description"),
        fields = $([]).add(name).add(description);

    $("#dialog_new_cluster").dialog({
        autoOpen: false,
        height: 330,
        width: 350,
        modal: true,
        resizable: false,
        buttons: {
            "Add new cluster": function() {
                fields.removeClass("ui-state-error");
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
                        CBMONITOR.configureCTree();
                        CBMONITOR.configureMEPanel();
                        $("#dialog_new_cluster").dialog("close");
                    },
                    error: function(jqXHR) {
                        CBMONITOR.highlightErrors(jqXHR, "c");
                    }
                });
            },
            Cancel: function() {
                fields.val("").removeClass("ui-state-error");
                $("#dialog_new_cluster").dialog("close");
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
        description = $("#description"),
        fields = $([]).add(address).add(rest_username).add(rest_password)
            .add(ssh_username).add(ssh_password).add(ssh_key).add(description);

    $("#dialog_new_server").dialog({
        autoOpen: false,
        resizable: false,
        height: 620,
        width: 400,
        modal: true,
        buttons: {
            "Add new server": function() {
                fields.removeClass("ui-state-error");
                var cluster = CBMONITOR.getSelectedParent();
                $.ajax({
                    type: "POST", url: "/cbmonitor/add_server/",
                    data: {
                        "address": address.val(),
                        "cluster": cluster.attr("id"),
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
                        $("#dialog_new_server").dialog("close");
                    },
                    error: function(jqXHR) {
                        CBMONITOR.highlightErrors(jqXHR, "");
                    }
                });
            },
            Cancel: function() {
                fields.val("").removeClass("ui-state-error");
                $("#dialog_new_server").dialog("close");
            }
        }
    });
};

CBMONITOR.addNewBucket = function() {
    "use strict";

    var jstree = $("#tree"),
        name = $("#bname"),
        type = $("input[name=btype]:checked"),
        port = $("#port"),
        password = $("#password"),
        fields = $([]).add(name).add(type).add(port).add(password);

    $("#bucket_type").buttonset();

    $("#dialog_new_bucket").dialog({
        autoOpen: false,
        resizable: false,
        height: 410,
        width: 350,
        modal: true,
        buttons: {
            "Add new bucket": function() {
                fields.removeClass("ui-state-error");
                var cluster = CBMONITOR.getSelectedParent();
                $.ajax({
                    type: "POST", url: "/cbmonitor/add_bucket/",
                    data: {
                        "name": name.val(),
                        "cluster": cluster.attr("id"),
                        "type": type.attr("id"),
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
                        $("#dialog_new_bucket").dialog("close");
                    },
                    error: function(jqXHR) {
                        CBMONITOR.highlightErrors(jqXHR, "b");
                    }
                });
            },
            Cancel: function() {
                fields.val("").removeClass("ui-state-error");
                $("#dialog_new_bucket").dialog("close");
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
                    prnt_cont = CBMONITOR.getSelectedParent(),
                    prev_cont = CBMONITOR.getSelectedParent(),
                    data,
                    url,
                    prnt;
                if (prnt_cont !== -1 && prev_cont !== -1) {
                    prnt = CBMONITOR.getSelectedParent(prnt_cont);
                }
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
                        data = {
                            "name": selected_id,
                            "cluster": prnt.attr("id")
                        };
                        url = "/cbmonitor/delete_bucket/";
                        break;
                    default:
                        break;
                }
                $.ajax({
                    type: "POST", url: url, data: data,
                    success: function(){
                        if (prnt_cont === -1 && prev_cont === -1) {
                            renc.addClass("ui-state-disabled");
                            delc.addClass("ui-state-disabled");
                            adds.addClass("ui-state-disabled");
                        }
                        jstree.jstree("remove", selected);
                        CBMONITOR.configureMEPanel();
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