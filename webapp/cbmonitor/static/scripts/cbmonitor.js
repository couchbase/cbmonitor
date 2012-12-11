$(document).ready(function(){
    $(function() {
        $( "#accordion" ).accordion({
            heightStyle: "fill"
        });
    });

    $(function() {
        $("button")
            .button()
            .css({
                fontSize: "77%",
                width: "32%"
            })
            .click(function( event ) {
                event.preventDefault();
            });
        $("input:text")
            .button()
            .css({
                fontSize: "77%",
                textAlign: "left",
                cursor : 'text'
            });
    });
});