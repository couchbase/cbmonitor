/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var SERIESLY = SERIESLY || {};


SERIESLY.Seriesly = function(db_name) {
    "use strict";

    this.db_name = db_name;
};


SERIESLY.Seriesly.prototype.biuldURL = function(args) {
    "use strict";

    var url = "/seriesly/" + this.db_name + "/_query?group=" + args.group;
    url = url + args.ptr;
    if (args.from) {
        url = url + "&from=" + args.from;
    }
    if (args.to) {
        url = url + "&to=" + args.to;
    }
    return url;
};


SERIESLY.Seriesly.prototype.query = function(args) {
    "use strict";

    var url = this.biuldURL(args),
        chart_data;

    $.ajax({url: url, dataType: "json", async: false,
        success: function(data) {
            chart_data = data;
        }
    });
    return chart_data;
};
