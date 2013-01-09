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

    for(var i = 0, l = args.ptrs.length; i < l; i++) {
        url = url + "&ptr=/" + args.ptrs[i] + "&reducer=avg";
    }
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

    var url = this.biuldURL(args);

    $.ajax({url: url, dataType: "json",
        success: function(data) {
            args.callback_object.init(data);
        }
    });
};
