$(document).ready(function() {



   $("[data-conferma]").each(function(i, e) {
        $(e).click(function() {
            return confirm($(e).data('conferma'));
        });
   });

   $("#benvenuto h1, #benvenuto h3").fadeIn(1500);

});