// field
let professione = $('#id_professione-autocomplete');
let specializzazione = $('#id_specializzazione-autocomplete');
let skill = $('#id_skill-autocomplete');
let area = $('#id_settore_di_riferimento');
let professione_value = $('#id_professione')
// let nuova_lingua = $('#id_nuova_lingua');

// blocchi
// let lingua_blocco = lingua.parent().parent();
// let nuova_lingua_blocco = nuova_lingua.parent();


// nuova_lingua_blocco.hide()
//
//
// no_lingua.on('change', function (e) {
//     if ($(this).is(':checked')) {
//         lingua_blocco.hide();
//         nuova_lingua_blocco.show();
//     } else {
//         lingua_blocco.show();
//         nuova_lingua_blocco.hide();
//     }
// });


$( document ).ready(function() {
    area.change(function() {
        professione.yourlabsAutocomplete().data = {
            'area': $(this).val()
        }
    });
    professione_value.change(function() {
        specializzazione.yourlabsAutocomplete().data = {
            'titolo_id': $(this).val()[0]
        }
        skill.yourlabsAutocomplete().data = {
            'titolo_id': $(this).val()[0]
        }
    });
});
