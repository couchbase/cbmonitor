/*jshint jquery: true, browser: true*/
/*global Spinner: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

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


CBMONITOR.Dialogs.prototype.configureAddNewSnapshot = function() {
    "use strict";

    var that = this,
        fields;

    fields = that.getFields(["name", "ts_from", "ts_to"]);
    $("#ts_from").datetimepicker({});
    $("#ts_to").datetimepicker({});

    $("#add_new_snapshot").dialog({
        autoOpen: false,
        resizable: false,
        height: 350,
        width: 350,
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

CBMONITOR.Dialogs.prototype.configureDeleteCluster = function() {
    "use strict";

    var that = this;
    $("#dialog_delete").dialog({
        autoOpen: false,
        resizable: false,
        height: 160,
        modal: true,
        buttons: {
            confirm: {
                "text": "Delete",
                "class": "btn btn-mini btn-dialog",
                "click": function() {
                    $.ajax({
                        type: "POST", url: "/cbmonitor/delete_cluster/",
                        data: {"name": that.to_remove},
                        success: function(){
                            location.reload();
                        }
                    });
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

CBMONITOR.Dialogs.prototype.addNewSnapshot = function() {
    "use strict";

    var that = this,
        name = $("#name"),
        ts_from = $("#ts_from"),
        ts_to = $("#ts_to");

    $.ajax({
        type: "POST", url: "/cbmonitor/add_snapshot/",
        data: {
            "name": name.val(),
            "cluster": $("#met_cluster").find(":selected").text(),
            "ts_from": ts_from.val(),
            "ts_to": ts_to.val()
        },
        success: function() {
            CBMONITOR.observables.updateClusters("metric");
            $("#add_new_snapshot").dialog("close");
        },
        error: function(jqXHR) {
            that.highlightErrors(jqXHR, "");
        }
    });
};
