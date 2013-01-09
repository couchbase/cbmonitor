/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var SERIESLY = SERIESLY || {};


SERIESLY.Seriesly = function(db_name) {
    "use strict";

    this.db_name = db_name;
};


SERIESLY.Seriesly.prototype.biuldURL = function(group, ptrs, from, to) {
    "use strict";

    var url = "/seriesly/" + this.db_name + "/_query?group=" + group;

    for(var i = 0, l = ptrs.length; i < l; i++) {
        url = url + "&ptr=/" + ptrs[i] + "&reducer=avg";
    }
    if (from) {
        url = url + "&from=" + from;
    }
    if (to) {
        url = url + "&to=" + to;
    }
    return url;
};


SERIESLY.Seriesly.prototype.query = function(group, ptrs, from, to, cb_object) {
    "use strict";

    var url = this.biuldURL(group, ptrs, from, to);

    $.ajax({url: url, dataType: "json",
        success: function(data) {
            cb_object.init(data);
        }
    });
};
