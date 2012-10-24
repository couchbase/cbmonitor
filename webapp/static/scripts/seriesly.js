"use strict";


var SERIESLY = SERIESLY || {};  // namespace


SERIESLY.Seriesly = function(db_name) {
    this.db_name = db_name;
};


SERIESLY.Seriesly.prototype.biuldURL = function(group, ptrs, from, to) {
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


SERIESLY.Seriesly.prototype.query = function(group, ptrs, from, to, object) {
    var url = this.biuldURL(group, ptrs, from, to);

    $.ajax({url: url, dataType: "json", success: function(data){
        object.handleData(data);
    }});
};
