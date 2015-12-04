$(document).ready(function() {

    $(function () {
        $('[data-toggle="popover"]').popover()
    })
    $("[data-conferma]").each(function(i, e) {
        $(e).click(function() {
            return confirm($(e).data('conferma'));
        });
    });
    $("[data-caricamento]").each(function(i, e) {

        if ($(e).is('form')) {
            $(e).submit(function() {
               $(e).find('[type="submit"]').addClass('disabled').find('.fa').addClass('fa-spin fa-spinner');
                return true;
            });
        } else {
           $(e).click(function() {
               var vecchioTesto = $(e).html()
               if ($(e).find('.fa')) {
                   $(e).find('.fa').addClass('fa-spin fa-spinner');
               } else {
                   $(e).html("<i class='fa fa-fw fa-spin fa-spinner'></i> Caricamento</i>");
               }
               $(e).addClass('disabled');
               setTimeout(function() {
                   $(e).removeClass('disabled');
                   $(e).html(vecchioTesto);
               }, 15000);
           })

        }
    });

   $("#benvenuto h1, #benvenuto h3").fadeIn(1500);
   $("#benvenuto p").fadeIn(3000);

    $(".autocomplete").removeAttr('required');

});