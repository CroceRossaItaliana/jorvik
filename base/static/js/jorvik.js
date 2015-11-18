$(document).ready(function() {

    $(function () {
         $('[data-toggle="popover"]').popover()
    })
   $("[data-conferma]").each(function(i, e) {
        $(e).click(function() {
            return confirm($(e).data('conferma'));
        });
   });

   $("#benvenuto h1, #benvenuto h3").fadeIn(1500);
   $("#benvenuto p").fadeIn(3000);

});