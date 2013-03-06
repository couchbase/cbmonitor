/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

/*
 * Modal dialogs for adding/removing clusters, servers, buckets
 */
CBMONITOR.Dialogs = function () {};

CBMONITOR.Dialogs.prototype.highlightErrors = function(jqXHR, prefix) {
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

CBMONITOR.Dialogs.prototype.adjustStyles = function() {
    "use strict";

    $(".text").css({"height": "12px", "fontSize": "77%"});
    $(".textarea").css({"fontSize": "77%"});
    $(".btradio").css({"width": "157px"});
    $("#Couchbase").button("toggle");
    $(".btn-dialog").css({"fontSize": "85%"});
};

CBMONITOR.Dialogs.prototype.getSelectedParent = function(selected) {
    "use strict";

    if (selected === undefined) {
        selected = $("#tree").jstree("get_selected");
    }
    return $.jstree._reference(selected)._get_parent(selected);
};

CBMONITOR.Dialogs.prototype.getFields = function(parameters) {
    "use strict";

    var parameter,
        fields = $([]);
    $.each(parameters, function(index, value) {
        parameter =  $("#" + value);
        fields.add(parameter);
    });
    return fields;
};

CBMONITOR.Dialogs.prototype.configureAddNewCluster = function() {
    "use strict";

    var that = this,
        fields;

    fields = this.getFields(["cname", "rest_username", "rest_password",
                             "master_node", "description"]);

    $("#dialog_new_cluster").dialog({
        autoOpen: false,
        height: 525,
        width: 350,
        modal: true,
        resizable: false,
        buttons: {
            confirm: {
                "text": "Add new cluster",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.removeClass("ui-state-error");
                    that.addNewCluster(fields);
                }
            },
            cancel: {
                "text": "Cancel",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.val("").removeClass("ui-state-error");
                    $("#dialog_new_cluster").dialog("close");
                }
            }
        },
        create: function () {
            that.adjustStyles();
        }
    });
};

CBMONITOR.Dialogs.prototype.configureAddNewServer = function() {
    "use strict";

    var that = this,
        fields;

    fields = this.getFields(["address", "ssh_username", "ssh_password",
                             "ssh_key", "description"]);

    $("#dialog_new_server").dialog({
        autoOpen: false,
        resizable: false,
        height: 550,
        width: 350,
        modal: true,
        buttons: {
            confirm: {
                "text": "Add new server",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.removeClass("ui-state-error");
                    that.addNewServer(fields);
                }
            },
            cancel: {
                "text": "Cancel",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.val("").removeClass("ui-state-error");
                    $("#dialog_new_server").dialog("close");
                }
            }
        },
        create: function () {
            that.adjustStyles();
        }
    });
};

CBMONITOR.Dialogs.prototype.configureAddNewBucket = function() {
    "use strict";

    var that = this,
        fields;

    fields = this.getFields(["bname", "bucket_type", "port", "password"]);

    $("#dialog_new_bucket").dialog({
        autoOpen: false,
        resizable: false,
        height: 410,
        width: 350,
        modal: true,
        buttons: {
            confirm: {
                "text": "Add new bucket",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.removeClass("ui-state-error");
                    that.addNewBucket();
                }
            },
            cancel: {
                "text": "Cancel",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.val("").removeClass("ui-state-error");
                    $("#dialog_new_bucket").dialog("close");
                }
            }
        },
        create: function () {
            that.adjustStyles();
        }
    });
};

CBMONITOR.Dialogs.prototype.configureAddNewSnapshot = function() {
    "use strict";

    var that = this,
        fields;

    fields = that.getFields(["name", "cluster", "ts_from", "ts_to"]);
    $("#ts_from").datetimepicker({});
    $("#ts_to").datetimepicker({});

    $("#add_new_snapshot").dialog({
        autoOpen: false,
        resizable: false,
        height: 450,
        width: 360,
        modal: true,
        buttons: {
            confirm: {
                "text": "Add new snapshot",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.removeClass("ui-state-error");
                    that.addNewSnapshot();
                }
            },
            cancel: {
                "text": "Cancel",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    fields.val("").removeClass("ui-state-error");
                    $("#add_new_snapshot").dialog("close");
                }
            }
        },
        create: function () {
            that.adjustStyles();
        }
    });
};

CBMONITOR.Dialogs.prototype.configureDeleteItem = function() {
    "use strict";

    var that = this;
    $("#dialog_delete").dialog({
        autoOpen: false,
        resizable: false,
        height:160,
        modal: true,
        buttons: {
            confirm: {
                "text": "Delete",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    that.deleteItem();
                    $(this).dialog("close");
                }
            },
            cancel: {
                "text": "Cancel",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    $(this).dialog("close");
                }
            }
        },
        create: function () {
            that.adjustStyles();
        }
    });
};

CBMONITOR.Dialogs.prototype.addNewCluster = function() {
    "use strict";

    var that = this,
        jstree = $("#tree"),
        name = $("#cname"),
        rest_username = $("#rest_username"),
        rest_password = $("#rest_password"),
        master_node = $("#master_node"),
        description = $("#description");

    var spinner = new Spinner({width: 4, top: "450px"});
    spinner.spin(document.getElementById('spinner'));

    $.ajax({
        type: "POST", url: "/cbmonitor/add_cluster/",
        data: {
            "name": name.val(),
            "rest_username": rest_username.val(),
            "rest_password": rest_password.val(),
            "master_node": master_node.val(),
            "description": description.val()
        },
        success: function(){
            spinner.stop();
            jstree.jstree("create", -1, "last",
                {
                    "attr": {"class": "cluster", "id": name.val()},
                    "data": name.val()
                },
                false, true
            );
            CBMONITOR.inventory.configureTree();
            $("#dialog_new_cluster").dialog("close");
        },
        error: function(jqXHR) {
            spinner.stop();
            that.highlightErrors(jqXHR, "c");
        }
    });
};

CBMONITOR.Dialogs.prototype.addNewServer = function() {
    "use strict";

    var that = this,
        jstree = $("#tree"),
        address = $("#address"),
        ssh_username = $("#ssh_username"),
        ssh_password = $("#ssh_password"),
        ssh_key = $("#ssh_key"),
        description = $("#description");
    var cluster = that.getSelectedParent();

    $.ajax({
        type: "POST", url: "/cbmonitor/add_server/",
        data: {
            "address": address.val(),
            "cluster": cluster.attr("id"),
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
            that.highlightErrors(jqXHR, "");
        }
    });
};

CBMONITOR.Dialogs.prototype.addNewBucket = function() {
    "use strict";

    var that = this,
        jstree = $("#tree"),
        name = $("#bname"),
        type = $("#bucket_type"),
        port = $("#port"),
        password = $("#password");
    var cluster = that.getSelectedParent();

    $.ajax({
        type: "POST", url: "/cbmonitor/add_bucket/",
        data: {
            "name": name.val(),
            "cluster": cluster.attr("id"),
            "type": type.children(".active").attr("id"),
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
            that.highlightErrors(jqXHR, "b");
        }
    });
};

CBMONITOR.Dialogs.prototype.addNewSnapshot = function() {
    "use strict";

    var that = this,
        name = $("#name"),
        cluster = $("#cluster"),
        ts_from = $("#ts_from"),
        ts_to = $("#ts_to");

    $.ajax({
        type: "POST", url: "/cbmonitor/add_snapshot/",
        data: {
            "name": name.val(),
            "cluster": cluster.val(),
            "ts_from": ts_from.val(),
            "ts_to": ts_to.val()
        },
        success: function() {
            CBMONITOR.snapshots.getClusters();
            $("#plot").removeClass("disabled");
            $("#pdf").removeClass("disabled");
            $("#add_new_snapshot").dialog("close");
        },
        error: function(jqXHR) {
            that.highlightErrors(jqXHR, "");
        }
    });
};

CBMONITOR.Dialogs.prototype.deleteItem = function() {
    "use strict";

    var that = this,
        jstree = $("#tree"),
        selected = jstree.jstree("get_selected"),
        selected_id = selected.attr("id"),
        selected_class = selected.attr("class").split(" ")[0],
        renc = $("#renc"),
        delc = $("#delc"),
        adds = $("#adds"),
        prnt_cont = that.getSelectedParent(),
        prev_cont = that.getSelectedParent(),
        data,
        url,
        prnt;
    if (prnt_cont !== -1 && prev_cont !== -1) {
        prnt = that.getSelectedParent(prnt_cont);
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
        }
    });
};