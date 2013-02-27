"use strict";

var reloadTimerId = null;
var oTable;
var colHdrs;     // e.g: ['sTitle': 'Testcase', 'sTitle': 'Env', ... ]
var rowHdrs;       // e.g: ['mixed-2suv', 'lucky6', ...]
var WARNING = 0.1;
var ERROR = 0.3;
var JIRA_PAT = /MB-([0-9])+|CBD-([0-9])+|CBSE-([0-9])+/gi;
var JIRA_URL = "http://www.couchbase.com/issues/browse/";

function setReloadInterval(itv_str) {
    if (isNaN(itv_str)) {
        console.error("cannot parse reload interval : " + itv_str);
        return;
    }

    var itv = parseInt(itv_str);

    // cancel reload events
    if (reloadTimerId !== null) {
        clearInterval(reloadTimerId);
    }

    if (itv !== 0) {
        reloadTimerId = setInterval(function() {
            location.reload();
        }, itv);
    }
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
        }, 'json');
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

function matchJiraTickets(text) {
    /**
     * Run regexp check and detect jira tickets
     * @return text with hyperlinkable jira tickets
     */
    if (text === undefined || !text) {
        return text;
    }

    var tickets = text.match(JIRA_PAT);
    if (!tickets) {
        return text;
    }

    $.each(tickets, function(i, v) {
        var url = JIRA_URL + v;
        text = text.replace(v, '<a href=' + url + '>' + v + '</a>');
    });

    return text;
}

function regTdActions(data, target, col, comment) {
    /**
     * Register actions to each table cell
     */
    var testcase= data[0];
    var env = data[1];
    var metric = data[2];
    var build = colHdrs[col]['sTitle'];

    if (col === 0) {
        var url = 'https://raw.github.com/couchbase/testrunner/master/conf/perf/' + testcase + '.conf';
        $(target).html(function(i, oldText) {
            return '<a href=' + url + '>' + oldText + '</a>';
        });
    }
    if (col < 4) {
        return;     // support test results for now
    }

    var rcMenu = [
        {'<div><div style="float:left;">Color: </div><div class="swatch" style="background-color:white"></div><div class="swatch" style="background-color:lightgreen"></div><div class="swatch" style="background-color:yellow"></div><div class="swatch" style="background-color:red"></div><div class="swatch" style="background-color:pink"></div></div><br>':
            function(menuItem, cmenu, e) {
                var t = $(e.target);
                if ($(t).is('.swatch')) {
                    var color = $(t).css('background-color');
                    $(target).css('background-color', color);
                    $(t).parent().find('.swatch').removeClass('swatch-selected');
                    $(t).addClass('swatch-selected');
                    $.ajax({
                        type: 'POST',
                        url: '../post/color/',
                        data: {'testcase': testcase,
                            'env': env,
                            'build': build,
                            'metric': metric,
                            'color': color},
                        error: function(response) {
                            console.error(response.responseText);
                        }
                    });
                }
            }
        },
        {'Comment': function(menuItem, cmenu, e) {
                $('#comment-form').dialog({
                    autoOpen: false,
                    modal: true,
                    width: 350,
                    buttons: {
                        Ok: function() {
                            var comment = $('#comment-form textarea').val();
                            $.ajax({
                                type: 'POST',
                                url: '../post/comment/',
                                data: {'testcase': testcase,
                                    'env': env,
                                    'build': build,
                                    'metric': metric,
                                    'comment': comment},
                                error: function(response) {
                                    console.error(response.responseText);
                                }
                            });
                            $(this).dialog("close");
                        },
                        Cancel: function() {
                            $(this).dialog("close");
                        }
                    },
                    open: function() {
                        if (comment === undefined) {
                            $('#comment-form textarea').val("");
                        } else {
                            $('#comment-form textarea').val(comment);
                        }
                    }
                });
                $("#comment-form").dialog("open");
            }
        }
    ];

    $(target).contextMenu(rcMenu , {theme:'gloss'});
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
        "fnStateSave": function (oSettings, oData) {
            localStorage.setItem('datatable', JSON.stringify(oData));
        },
        "fnStateLoad": function (oSettings) {
            return JSON.parse(localStorage.getItem('datatable'));
        },
        'fnDrawCallback': function() {
            $('#loading').remove();
        },
        "aoColumnDefs": [ {
            "aTargets": [ '_all' ],
            "mRender": function ( data, type, full ) {
                var arr = data.split("-&-");
                return arr[0];
            },
            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                var arr = oData[iCol].split("-&-");
                if (typeof(arr[1]) !== undefined && arr[1]) {
                    $(nTd).css('background-color', arr[1]);
                }
                if (typeof(arr[2]) !== undefined && arr[2]) {
                    var comment = matchJiraTickets(arr[2]);
                    $(nTd).append("<div class='comment'>" + comment + "</div>");
                }
                regTdActions(oData, nTd, iCol, arr[2]);
            }
        }],
        'bDestroy': true,
        "bAutoWidth": false,
        "bSortClasses": false
    });

    new FixedHeader(oTable);

    $('td', oTable.fnGetNodes()).hover(function() {
        var iCol = $('td').index(this) % colHdrs.length;
        var nTrs = oTable.fnGetNodes();
        $('td:nth-child('+(iCol+1)+')', nTrs).addClass('hovered');
    }, function() {
        $('td.hovered', oTable.fnGetNodes()).removeClass('hovered');
    });

}
