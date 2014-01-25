/*jshint jquery: true, browser: true*/

var CBMONITOR = CBMONITOR || {};

$(document).ready(function(){
    "use strict";

    CBMONITOR.configureAccordion();

    CBMONITOR.observables = new CBMONITOR.Observables();
    CBMONITOR.observables.updateSelectors();

    CBMONITOR.graphManager = new CBMONITOR.GraphManager();

    CBMONITOR.views = new CBMONITOR.Views();
    CBMONITOR.views.configurePanel();
    CBMONITOR.views.enableDroppable();

    CBMONITOR.snapshots = new CBMONITOR.Snapshots();
});