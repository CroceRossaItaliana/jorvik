$(document).ready(function() {
    $(function () {
        $('[data-toggle="popover"]').popover()
    })
    $("[data-conferma]").each(function(i, e) {
        $(e).click(function() {
            return confirm($(e).data('conferma'));
        });
    });
    $("[data-alert]").each(function(i, e) {
        $(e).click(function() {
            alert($(e).data('alert'));
            return true;
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

    tinymce.init({
        selector: ".wysiwyg-semplice",
        relative_urls: false,
        toolbar: 'undo redo | bold italic | link unlink image | table | bullist numlist outdent indent',
        statusbar: false,
        plugins: 'link image table',
        menubar: false,
        language: 'it',
        resize: 'both',
    });

    // Datetime pickers
    $.datetimepicker.setLocale('it');

    $(".selettore-data").datetimepicker({
        format:'d/m/Y',
        timepicker: false,
        dayOfWeekStart: 1,
        scrollMonth : false,
        scrollInput : false,
    });

    $(".selettore-data-ora").datetimepicker({
        format:'d/m/Y H:i',
        dayOfWeekStart: 1,
        scrollMonth : false,
        scrollInput : false
    });

    $("#selettore-data-mese-anno").datetimepicker({
        format:'m-Y',
        changeMonth: true,
        changeYear: true,
        scrollMonth : false,
        scrollInput : false,
    });
});

// Funzione per autoscroll.
//   es. $(document).load(function() { autoscroll("#turno-123"); });
function autoscroll(id) {
    var $anchor = $(id).offset();
    var top = Math.max(0, ($anchor.top - $("#navbar").height()));
    $('body').animate({ scrollTop: top }, 800);
    return false;
}

// Collapsible menus in the left sidebar
// template: anagrafica/templates/anagrafica_utente_vuota.html
var css_class = 'collapsible-menu-active';
var current_page_nav = $('.active').closest('ul');
var prev_elem = null;

// Show and hide various menus by default
var all_menu = $('.collapsible-menu-ul');
var all_menu_titles = $('.collapsible-menu-title');
var menu_persona = $(all_menu_titles).filter(":contains('Persona')");
var menu_links = $(all_menu_titles).filter(":contains('Links')");
all_menu.hide();

$('#sezione[data-nav-ul="'+menu_persona.data('nav-id')+'"]').show();
$('#sezione[data-nav-ul="'+menu_links.data('nav-id')+'"]').show();
current_page_nav.show();

// sync with base/menu.py
$('ul li[role=presentation]').filter(":contains('Portale convenzioni')").css({'font-weight': 'bold'});

$('.collapsible-menu-title').on('click', function(){
    let data_nav_id = $(this).data('nav-id');
    if (prev_elem) {
        prev_elem.removeClass(css_class);
    }
    prev_elem = $(this);
    all_menu.hide();
    $('[data-nav-ul='+data_nav_id+']').show();
    $(this).addClass(css_class);
});


var corporate_benefits_link = $('ul li[role=presentation]').filter(":contains('Corporate benefits')");
var portale_italo_link = $('ul li[role=presentation]').filter(":contains('Portale Italo')");

$(corporate_benefits_link).add(portale_italo_link).on('click', function(e){
    e.preventDefault();
    let _thiz = $(this);
    let link_text = _thiz.text().trim();
    _thiz.attr({
        'data-toggle': "modal",
        'data-target': "#privacy_modal",
    });
    if (link_text == 'Corporate benefits') {
        _thiz.attr('data-redirect', 'https://cri.convenzioniaziendali.it');
    } else if (link_text == 'Portale Italo') {
        _thiz.attr('data-redirect', 'https://criv.simplecrs.it/oauth2/crocerossa');
    }
});

$(function(){
    var redirectUrl = '';
    $('#privacy_modal').on('show.bs.modal', function (event) {
         redirectUrl=$(event.relatedTarget).attr('data-redirect');
    });

    var onConfirmClicked = function(){
        window.open(redirectUrl, '_blank');
        $('#privacy_modal').modal('toggle');
    };
});