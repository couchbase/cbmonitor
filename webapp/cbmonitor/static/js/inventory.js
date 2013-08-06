/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

CBMONITOR.Inventory = function () {
    "use strict";

    $(".icon-remove").click(function() {
        $("#dialog_delete").dialog("open");
        CBMONITOR.dialogs.to_remove = this.id;
    });
};


$(document).ready(function(){
    "use strict";

    CBMONITOR.inventory = new CBMONITOR.Inventory();

    CBMONITOR.dialogs = new CBMONITOR.Dialogs();
    CBMONITOR.dialogs.configureDeleteCluster();
});