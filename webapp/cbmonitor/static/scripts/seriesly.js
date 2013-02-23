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
        item = ui.draggable.text();

    var url = "/seriesly/" + cluster + "/_query?group=10000";
    url += "&ptr=/samples/" + item + "&reducer=avg";
    url += "&f=/meta/bucket&fv="; url += bucket.length ? bucket : "none";
    url += "&f=/meta/server&fv="; url += server.length ? server : "none";

    return url;
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
