"use strict";

var oTable;
var colHdrs = [];       // e.g: ['sTitle': 'Testcase', 'sTitle': 'Env', ... ]
var rowHdrs = [];       // e.g: ['mixed-2suv', 'lucky6', ...]
var baselines = [];
var WARNING_RANGE = 0.1;
var ERROR_RANGE = 0.3;           // TODO: user define

function createSettings() {
    /*
     * Create user setting table
     *
     * The first two columns are reserved for build infos and timestamps
     * Actual settings starts from column 3
     */
    var buildList = '';
    var content = '';

    $.each(colHdrs.slice(2), function(j, build) {
        buildList += '<option value="' + build.sTitle + '">';
        buildList +=  build.sTitle + '</option>';
    });

    $.each(rowHdrs, function(i, metric) {
        content += '<tr><td>' + metric + '</td>';
        content += '<td><select>' + buildList + '</select></td></tr>';
    });

    return content;
}

function saveSettings() {
    /*
     * Save user defined settings to cookie
     */
    $('#settings table tbody tr').each(function(i) {
        var col = $(this).find('td').eq(0).text();
        var build = $(this).find("select option:selected").text();
        $.cookie(col, build, { expires: 14 });
        oTable.$('tr').each(function() {
            var row = oTable.fnGetData(this);
            if (row[0] === build) {
                baselines[i] = parseInt(row[2+i]);
            }
        });
    });
}

function getSettings() {
    /*
     * Get user defined settings
     */
    $('#settings table tbody tr').each(function(i) {
        var col = $(this).find('td').eq(0).text();
        var build = $.cookie(col);
        if (build !== null) {
            $(this).find('select option').filter(function() {
                return $(this).text() === build;
            }).attr('selected', true);
        } else {
            build = $(this).find("select option:selected").text();
        }
        oTable.$('tr').each(function() {
            var row = oTable.fnGetData(this);
            if (row[0] === build) {
                baselines[i] = parseInt(row[2+i]);
            }
        });
    });
}

function applyErrorRanges() {
    /*
     * Apply error range check for each cell
     *
     * If data falls out of the range, turns cell to red
     * Accept negative ranges
     */
    oTable.$('tr').each(function() {
        var row = $(this);
        var vals = oTable.fnGetData(this);
        $.each(vals.slice(2), function(j, v) {
            v = parseInt(v);
            $(row).find('td').eq(j+2).removeAttr("style");
            if (!isNaN(baselines[j]) && !isNaN(v)) {
                var delta = (v - baselines[j]) / baselines[j];
                if (Math.abs(ERROR_RANGE) < Math.abs(WARNING_RANGE)) {
                    console.log("invalid error/warning ranges");
                    return;
                }
                if ((delta > ERROR_RANGE && ERROR_RANGE > 0) ||
                    (delta < ERROR_RANGE && ERROR_RANGE < 0)) {
                    $(row).find('td').eq(j+2).css("background-color","red");
                } else if ((delta > WARNING_RANGE && delta < ERROR_RANGE) ||
                           (delta < WARNING_RANGE && delta > ERROR_RANGE)) {
                    $(row).find('td').eq(j+2).css("background-color","yellow");
                }
            }
        });
    });
}

function processData(data) {
    /*
     * Process json data coming from the server
     * Current implementation retrieves info only
     */
    $.each(data[0], function(i, v) {
        colHdrs[i] = {'sTitle': v};
    });

    $.each(data.slice(1), function(i, v) {
        rowHdrs[i] = v[0];
    });

    return data;
}

function renderTable(data) {
    /*
     * Render table with the given data
     */

    oTable = $('#litmus table').dataTable({
        "sDom": 'Tlfrtip',
        'bProcessing': true,
        'bPaginate': true,
        'sPaginationType': 'full_numbers',
        'aaData': data.slice(1),
        'aoColumns': colHdrs,
        'aaSorting': [[0, 'desc']],
        'bStateSave': true,
        'fnDrawCallback': function() {
            $('#loading').remove();
        }
    }).bind('sort', function () {
        applyErrorRanges();
    });

    oTable.$('td').each(function() {
        var pos = oTable.fnGetPosition(this);
        if (pos[1] < 4) {
            return;     // support test results for now
        }
        var testcase= data[pos[0] + 1][0];
        var env = data[pos[0] + 1][1];
        var metric = data[pos[0] + 1][2];
        var build = colHdrs[pos[1]]['sTitle'];
        $(this).qtip({
            content: {
                text: 'Loading...',
                ajax: {
                    url: '../get/comment',
                    type: 'GET',
                    loading: false,
                    data: {'testcase': testcase,
                           'env': env,
                           'build': build,
                           'metric': metric},
                    success: function(data, status) {
                        this.set('content.text', data);
                    }
                }
            },
            position: {
                at: 'bottom left',
                my: 'top left'
            },
            style: {
                classes: 'qtip-shadow'
            }
        });
    });
}
