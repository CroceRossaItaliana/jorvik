// field
let lingua = $('#id_lingua-autocomplete');
let no_lingua = $('#id_no_lingua');
let nuova_lingua = $('#id_nuova_lingua');

// blocchi
let lingua_blocco = lingua.parent().parent();
let nuova_lingua_blocco = nuova_lingua.parent();


nuova_lingua_blocco.hide()


no_lingua.on('change', function (e) {
    if ($(this).is(':checked')) {
        lingua_blocco.hide();
        nuova_lingua_blocco.show();
    } else {
        lingua_blocco.show();
        nuova_lingua_blocco.hide();
    }
});

