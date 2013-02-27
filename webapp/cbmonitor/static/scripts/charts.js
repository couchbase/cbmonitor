/*jshint jquery: true, browser: true*/

/*
 * Name space
 */
var CBMONITOR = CBMONITOR || {};

/*
 * Accordion with clusters/metrics/events
 */
CBMONITOR.configureAccordion = function() {
    "use strict";

    $("#accordion").accordion({
        heightStyle: "fill"
    });
};

$(document).ready(function(){
    "use strict";

    CBMONITOR.configureAccordion();

    CBMONITOR.observables = new CBMONITOR.Observables();
    CBMONITOR.observables.updateSelectors();

    CBMONITOR.graphManager = new CBMONITOR.GraphManager();

    CBMONITOR.views = new CBMONITOR.Views();
    CBMONITOR.views.configurePanel();
    CBMONITOR.views.enableDroppable();
});