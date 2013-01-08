"use strict";

var oTable;
var colHdrs;     // e.g: ['sTitle': 'Testcase', 'sTitle': 'Env', ... ]
var rowHdrs;       // e.g: ['mixed-2suv', 'lucky6', ...]
var BASELINE = "1.8.1-938-rel-enterprise";
var WARNING = 0.1;
var ERROR = 0.3;

function Settings(testcase, metric) {
    this.testcase = testcase;
    this.metric = metric;
    this.baseline = BASELINE;
    this.error = ERROR;
    this.warning = WARNING;
}

function getSettings(settings) {
    /*
     * Get user defined settings
     */
    $.get('/litmus/get/settings',
        {'testcase': settings.testcase, 'metric': settings.metric},
        function(data) {
            settings.error = data.error;
            settings.warning = data.warning;
            settings.baseline = data.baseline;
        }, 'json');
}

function getAllTags() {
    $.get('/litmus/get/tags',
        function(data) {
            $.each(data, function(i, v) {
                // input(type='radio', name='tag', onclick="showResults('');", id="2.0.1")label(for="2.0.1") 2.0.1
                var button = "<input type='radio' name='tag' onclick=\"showResults('" + v + "');\" id='"
                             + v.replace(/\./g, '-')  + "'><label for='"
                             + v.replace(/\./g, '-') + "'>" + v + "</label>";
                $('#tag').append(button);
            });
            $(function() {
                $("#tag").buttonset();
            });
        }, 'json');

}

function showResults(tag) {
    var url, oTable;
    if (tag) {
        url = '/litmus/get?tag=';
    } else {
        url = '/litmus/get?';
    }
    $.get(url + tag, { },
        function(data) {
            processData(data);
            renderTable(data);
            applyErrorRanges();
        }, 'json');
}

function changeColors(row, vals, error, warning) {
    /**
     * Change cell colors based on the baseline values
     */
    return function(data) {
        if (data.length === 1) {
            return;
        }
        var baseval = data[1][4];
        $.each(vals.slice(4), function(j, v) {
            v = parseInt(v);
            $(row).find('td').eq(j+4).removeAttr("style");
            if (!isNaN(baseval) && !isNaN(v)) {
                var delta = (v - baseval) / baseval;
                if (Math.abs(error) < Math.abs(warning)) {
                    console.error("invalid error/warning ranges");
                    return;
                }
                if ((delta > error && error > 0) ||
                    (delta < error && error < 0)) {
                    $(row).find('td').eq(j+4).css("background-color","red");
                } else if ((delta > warning && delta < error) ||
                    (delta < warning && delta > error)) {
                    $(row).find('td').eq(j+4).css("background-color","yellow");
                }
            }
        });
    };
}
function applyErrorRanges() {
    /*
     * Apply error range check for each cell
     *
     * If data falls out of the range, turns cell to red
     * Accept negative ranges
     */
    oTable.$('tr').each(function() {
        var row = this;
        var vals = oTable.fnGetData(this);
        var settings = new Settings(vals[0], vals[2]);
        getSettings(settings);
        var uri = '/litmus/get';
        var criteria = {'testcase': settings.testcase,
                        'metric': settings.metric,
                        'build': settings.baseline,
                        'env': vals[1]};
        $.get(uri, criteria,
              changeColors(row, vals, settings.error, settings.warning),
              'json');
    });
}

function processData(data) {
    /*
     * Process json data coming from the server
     * Current implementation retrieves info only
     */
    colHdrs = [];
    rowHdrs = [];
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

    if (oTable) {
        oTable.fnDestroy();
        $("thead").remove();
    }

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
        },
        'bDestroy': true,
        "bAutoWidth": false
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
                        if ($.trim(data).length === 0) {
                            this.set('content.text', 'Click to edit comment');
                        } else {
                            this.set('content.text', data);
                        }
                    },
                    error: function(response) {
                        console.error(response.responseText);
                        this.set('content.text', 'Click to edit comment');
                    }
                }
            },
            position: {
                at: 'bottom center',
                my: 'top left'
            },
            show: {
                solo: true
            },
            hide: 'unfocus',
            style: {
                classes: 'qtip-shadow'
            },
            events: {
                focus: function(event, api) {
                    $(this).find('.qtip-content').editable( '../post/comment/', {
                        submitdata: function (value, settings) {
                            return {
                                "testcase": testcase,
                                "env": env,
                                "metric": metric,
                                "build": build,
                                "comment": $('input[name=value]').val()
                            };
                        },
                        height: '14px',
                        width: '100%'
                    });
                }
            }
        });

        $(this).spectrum({
            showPalette: true,
            palette: [
                ['white'],
                ['red', 'yellow', 'green'],
                ['pink', 'lightyellow', 'lightgreen']
            ],
            localStorageKey: "litmus.dashboard",
            showInput: true,
            change: function(color) {
                $(this).css('background-color', color.toHexString());
            }
        });
    });

    new FixedHeader(oTable);
}
