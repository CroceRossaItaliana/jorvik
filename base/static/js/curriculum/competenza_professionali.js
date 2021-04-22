// fields
let professione = $('#id_professione-autocomplete');
let no_professione = $('#id_no_professione');
let nuova_professione = $('#id_nuova_professione');

let specializzazione = $('#id_specializzazione-autocomplete');
let no_specializzazione = $('#id_no_specializzazione');
let nuova_specializzazione = $('#id_nuova_specializzazione');

let skill = $('#id_skill-autocomplete');
let no_skill = $('#id_no_skill');
let nuova_skill = $('#id_nuova_skill');

let area = $('#id_settore_di_riferimento');
let professione_value = $('#id_professione');

// blocchi
let professione_blocco = professione.parent().parent();
let nuova_professione_blocco = nuova_professione.parent();

let specializzazione_blocco = specializzazione.parent().parent();
let nuova_specializzazione_blocco = nuova_specializzazione.parent();

let skill_blocco = skill.parent().parent();
let nuova_skill_blocco = nuova_skill.parent();


nuova_professione_blocco.hide();
nuova_specializzazione_blocco.hide();
nuova_skill_blocco.hide()


$( document ).ready(function() {
    area.change(function() {
        professione.yourlabsAutocomplete().data = {
            'area': $(this).val()
        }
    });
    professione_value.change(function() {
        specializzazione.yourlabsAutocomplete().data = $(this).val() !== null ? {'titolo_id': $(this).val()[0]} : {}
        skill.yourlabsAutocomplete().data =  $(this).val() !== null ? {'titolo_id': $(this).val()[0]} : {}
    });
});

no_professione.on('change', function (e) {
    if ($(this).is(':checked')) {
        professione_blocco.hide();
        nuova_professione_blocco.show();
    } else {
        professione_blocco.show();
        nuova_professione_blocco.hide();
    }
});

no_specializzazione.on('change', function (e) {
    if ($(this).is(':checked')) {
        specializzazione_blocco.hide();
        nuova_specializzazione_blocco.show();
    } else {
        specializzazione_blocco.show();
        nuova_specializzazione_blocco.hide();
    }
});

no_skill.on('change', function (e) {
    if ($(this).is(':checked')) {
        nuova_skill_blocco.show();
    } else {
        nuova_skill_blocco.hide();
    }
});
