// field
let auto_diploma = $('#id_diploma');
let no_diploma = $('#id_no_diploma');
let nuovo_diploma = $('#id_nuovo_diploma');

let auto_laurea = $('#id_laurea');
let no_laurea = $('#id_no_laurea');
let nuovo_laurea = $('#id_nuova_laurea');

// blocchi
let auto_diploma_blocco = auto_diploma.parent().parent();
let no_diploma_blocco = no_diploma.parent();
let nuovo_diploma_blocco = nuovo_diploma.parent();

let auto_laurea_blocco = auto_laurea.parent().parent();
let no_laurea_blocco = no_laurea.parent();
let nuovo_laurea_blocco = nuovo_laurea.parent();


auto_diploma_blocco.hide();
no_diploma_blocco.hide();
nuovo_diploma_blocco.hide();

auto_laurea_blocco.hide();
no_laurea_blocco.hide();
nuovo_laurea_blocco.hide();

let titolo_di_studio = $('#id_tipo_titolo_di_studio');

titolo_di_studio.change(function () {
    let select_val = $(this).val();
    if (select_val === "DI") {
        auto_diploma_blocco.show();
        no_diploma_blocco.show();
        nuovo_diploma_blocco.hide();

        auto_laurea_blocco.hide();
        no_laurea_blocco.hide();
        nuovo_laurea_blocco.hide();
    }
    else if (select_val !== "DI" && select_val !== "SO"){
        auto_diploma_blocco.hide();
        no_diploma_blocco.hide();
        nuovo_diploma_blocco.hide();

        auto_laurea_blocco.show();
        no_laurea_blocco.show();
        nuovo_laurea_blocco.hide();

    }
    else{
        auto_diploma_blocco.hide();
        no_diploma_blocco.hide();
        nuovo_diploma_blocco.hide();

        auto_laurea_blocco.hide();
        no_laurea_blocco.hide();
        nuovo_laurea_blocco.hide();
    }
})

no_diploma.on('change', function (e) {
    if ($(this).is(':checked')) {
        auto_diploma_blocco.hide();
        nuovo_diploma_blocco.show();
    } else {
        auto_diploma_blocco.show();
        nuovo_diploma_blocco.hide();
    }
});


no_laurea.on('change', function (e) {
    if ($(this).is(':checked')) {
        auto_laurea_blocco.hide();
        nuovo_laurea_blocco.show();
    } else {
        auto_laurea_blocco.show();
        nuovo_laurea_blocco.hide();
    }
});




