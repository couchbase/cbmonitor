/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var SERIESLY = SERIESLY || {};


SERIESLY.Seriesly = function(db_name) {
    "use strict";

    this.db_name = db_name;
};


SERIESLY.Seriesly.prototype.biuldURL = function(ui) {
    "use strict";

    var cluster = ui.draggable.attr("cluster"),
        server = ui.draggable.attr("server"),
        bucket = ui.draggable.attr("bucket"),
        collector = ui.draggable.attr("collector"),
        item = ui.draggable.text();

    var db_name = collector.length ? collector.replace(/\./g, "") : "";
    db_name += cluster;
    db_name += bucket.length ? bucket.replace(/\./g, "") : "";
    db_name += server.length ? server.replace(/\./g, "") : "";

    return "/seriesly/" + db_name + "/_query?group=5000" +
        "&ptr=/" + item + "&reducer=avg";
};


SERIESLY.Seriesly.prototype.query = function(ui) {
    "use strict";

    var url = this.biuldURL(ui),
        chart_data;

    $.ajax({url: url, dataType: "json", async: false,
        success: function(data) {
            chart_data = data;
        }
    });
    return chart_data;
};
