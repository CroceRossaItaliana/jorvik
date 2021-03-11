// field
let auto_diploma = $('#id_diploma');
let no_diploma = $('#id_no_diploma');
let nuovo_diploma = $('#id_nuovo_diploma');

// blocchi
let auto_diploma_blocco = auto_diploma.parent().parent();
let no_diploma_blocco = no_diploma.parent();
let nuovo_diploma_blocco = nuovo_diploma.parent();

auto_diploma_blocco.hide();
no_diploma_blocco.hide();
nuovo_diploma_blocco.hide();


let titolo_di_studio = $('#id_titolo_di_studio');

titolo_di_studio.change(function () {
    let select_val = $(this).val();
    if (select_val === "2") {
        auto_diploma_blocco.show();
        no_diploma_blocco.show();
        nuovo_diploma_blocco.hide();
    }else{
        auto_diploma_blocco.hide();
        no_diploma_blocco.hide();
        nuovo_diploma_blocco.hide();
    }
})






