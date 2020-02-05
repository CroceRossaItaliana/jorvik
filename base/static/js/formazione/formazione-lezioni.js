// Listing lezioni (url: aspirante/corso-base/<id>>/lezioni/)
$('.toggleLezione').on('click', function(e){
    let lezione_id = $(this).data('lezione-id');
    let TOGGLE_BG_CLASS = "toggle-bg";

    $('.lezione-head').removeClass(TOGGLE_BG_CLASS);
    $('.lezione-data').hide();
    $(lezione_id).toggle();

    let tr_parent = $(this).closest('tr');

    if ( !tr_parent.hasClass(TOGGLE_BG_CLASS)  ) {
        $(tr_parent).addClass(TOGGLE_BG_CLASS);
    } else {
        $(tr_parent).removeClass(TOGGLE_BG_CLASS);
    }
});


// Nascondi gli input senza valore
$('.docente_esterno_hidden').parent('div.form-group').hide();

// Aggancia una funzione all'event
$('.show_docente_esterno').on('click', function(e) {
    let lezione_id = $(this).data('id');
    let docente_esterno_input = $('#id_'+ lezione_id +'-docente_esterno');
    let docente_esterno_form_group = docente_esterno_input.parent('div.form-group');

    if ( docente_esterno_form_group.is(':visible') ) {
        docente_esterno_form_group.hide();
    } else {
        docente_esterno_form_group.show();
    }
});


// Gestione presenze
$('.esoneroCheckbox').on('click', function(e){
    let esonero_id = $(this).data('esonero');
    $(esonero_id).toggle();

	if ($(this).is(":checked")) {
		$(this).prop('checked', 'checked');
	} else {
		$(this).prop('checked', '');
	};


	// checkbox "Presenza"
	let presenza_lezione_partecipante = $(this).data('lezione-partecipante')
	let checkbox_presenza = $('#presenza-' +presenza_lezione_partecipante);

	if (checkbox_presenza.prop('checked')) {
	// if ($(this).prop('checked') === false) {
	//  checkbox_presenza.prop('checked', '');
	// }
	} else {
		checkbox_presenza.prop('checked', 'checked');
	}
});
