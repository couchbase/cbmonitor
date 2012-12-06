$(document).ready(function(){
    $('#search').submit(function(event){
        // Clean and hide results container
        var results = $('#results');
        results.empty();
        results.css("visibility", "hidden");

        // Show spinner
        var opts = {width: 4, top: "-30px", color: "#b7ddf2"};
        var target = document.getElementById("spinner");
        var spinner = new Spinner(opts).spin(target);

        // Fetch list of pdf reports
        var testcase = $('#testcase').val();
        var build = $('#build').val();
        var url = "/reports/search?testcase=" + testcase + "&build=" + build;
        $.ajax({url: url, dataType: "json", success: function(data){
            // Hide spinner
            spinner.stop();

            // Show list of links or warning message
            results.css("visibility", "visible");
            if (data.length) {
                for(var i=0, len=data.length; i < len; i++) {
                    var newlink = '<a href="' + data[i][1] + '">' + data[i][0] + '</br>';
                    results.append(newlink);
                }

            } else {
                results.html("<p>Not found</p>");
            }
        }, error: function(jqXHR, textStatus, errorThrown) {
            // Hide spinner
            spinner.stop();

            // Show error message
            results.css("visibility", "visible");
            results.html("<p>" + errorThrown + "</p>");
        }});

        // Disable auto-refresh
        event.preventDefault();
    });
});