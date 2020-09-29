// Parent template: formazione_corsi_base_nuovo.html

$('#formazioneCorsoNuovoForm').trigger("reset");

// Select: Tipo -> Show "Tipo del Corso" field
var titolo_form_group = $('#id_titolo_cri').closest('.form-group');
var level_form_group = $('#id_level').closest('.form-group');
var area_form_group = $('#id_area').closest('.form-group');
var corso_base_tipo_value = 'BA';
var corso_nuovo_tipo_value = 'C1';
var corso_online_value = 'CO';
var titolo_options_ajax_data = {};


function showDeliberaFileLink(corso_tipo_selected, value="") {
    if (!value) return;
    if (!corso_tipo_selected) return;

    const DATAFILES_URL = "https://datafiles.gaia.cri.it/media/filer_public";

    let delibere = {
        '1': "/df/ac/dfac11b1-419e-4ba7-b085-ab763fe1424c/corso-delibera-1.docx",
        '2': "/7a/f4/7af45b08-cd70-49fa-9342-34e0b029acb2/corso-delibera-2.docx",
        '3': "/c1/60/c1605890-e11c-4e65-94d9-812b2683ca00/corso-delibera-3.docx",
        '4': "/e2/85/e285dbc2-cd51-4d1a-926c-fa787a0637ac/corso-delibera-4.docx",
        '5': "/22/76/2276bb48-2a11-4b92-94fb-1ae731f586b5/corso-delibera-5.docx",
    };

    let delibera_label = $('label[for="id_delibera_file"]');
    let delibera_file_url = "";
    let html_to_append = "";

    if (corso_tipo_selected == corso_base_tipo_value) {
        delibera_file_url = delibere['1'];
    }

    if (corso_tipo_selected == corso_nuovo_tipo_value) {
        if (value === "1") delibera_file_url = delibere['2'];
        else if (value === "2") delibera_file_url = delibere['3'];
        else if (value === "3") delibera_file_url = delibere['4'];
        else if (value === "4") delibera_file_url = delibere['5'];
        // else if (value === "firstAvailable") delibera_file_url = $('#id_leveloption:first').val();
    }

    if (!delibera_file_url) return;

    cleanDeliberaFileLink();

    delibera_label.append("<div id='delibera_file_link'><a href='"+DATAFILES_URL + delibera_file_url+"' target='_blank'>Scarica delibera</a></div>");
}

function cleanDeliberaFileLink() {
    let delibera_file_link = $('#delibera_file_link');
    if (delibera_file_link.length) {
        delibera_file_link.remove();
    }
}

// Mostra tutta (non nascondi come di default) la sezione con la form di attivazione se
// la form ha dei dati inseriti e c'è qualche errore di validazione da mostrare.
if ($('#id_tipo option:selected').val()) {
    $('.attivazionePanelWithForm').show();
}

if ($('#id_tipo option:selected').val() != corso_nuovo_tipo_value) {
    titolo_form_group.hide();
    level_form_group.hide();
    area_form_group.hide();
}

$('#id_tipo').on('change', function(e){
    let corso_tipo_value = $(this).find('option:selected').val();

    $('#id_level').prop('selectedIndex',0); // reset voce selezionata nell'area

    if (corso_tipo_value) {
        showDeliberaFileLink(corso_tipo_value, "1"); //, "firstAvailable");
    } else {
        cleanDeliberaFileLink();
    }

    if (corso_tipo_value && (corso_tipo_value == corso_nuovo_tipo_value || corso_tipo_value == corso_online_value)){
        level_form_group.show();
        area_form_group.show();
    }
    else {
        titolo_form_group.hide();
        level_form_group.hide();
        area_form_group.hide();
    }
});

$('#id_area').on('change', function(e){
    let value = $(this).find('option:selected').val();

    if (value) {
        titolo_form_group.show();
    } else {
        titolo_form_group.hide();
    }
});

// Select: Livello
$('#id_level').on('change', function(e){
    let corso_tipo_value = $('#id_tipo').find('option:selected').val();
    let value = $(this).val();

    // Reset area's selected option and hide its section
    $('#id_area').prop('selectedIndex',0);
    titolo_form_group.hide();

    if (value) {
        area_form_group.show();
        showDeliberaFileLink(corso_tipo_value, value);
    }
});

// Select: Area
var select_area = $('#id_area');
if (!select_area.prop('selectedIndex')) {
  select_area.prop('selectedIndex',0);
}

$('#id_titolo_cri').find('option').not(':first').remove();
$('#id_area').on('change', function(e) {
    let area_id = $(this).val();
    let id_level_val = $('#id_level').val(); // default select option has '' value
    if (area_id !== '') {
        $.ajax({
            type: "POST",
            url: url_cv_cdf_titolo_json,
            data: {
                area: area_id,
                cdf_livello: id_level_val,
                tipo: $('#id_tipo').val(),
                csrf_token: _csrf_token,
            },
            success: function(data) {
                let select_titolo_cri = $('#id_titolo_cri');
                select_titolo_cri.find('option').not(':first').remove();

                titolo_options_ajax_data = data;

                $.each(data, function(id, text) {
                    select_titolo_cri.append($('<option>', {
                        value: id,
                        text: text['nome'],
                    }));
                });

                return data;
            },
            error: function(jqXHR, textStatus) {
                <!--console.log(textStatus);-->
            },
        });

    } else {
        titolo_form_group.hide();
        $('#id_titolo_cri').find('option').not(':first').remove();
    }
});


// GAIA-89
// Add titles: description under the <select> element
function resetDescriptionDiv(){
    let description_div = $('#titleDescription');
    if (description_div.length) {
        description_div.remove();
    }
};

$('#id_tipo, #id_level, #id_area').on('change', function(e){
    resetDescriptionDiv();
});

$('#id_titolo_cri').on('change', function(e) {
    resetDescriptionDiv();

    let selected_option_id = $(this).val();
    let title = titolo_options_ajax_data[selected_option_id];
    if ('description' in title && title['description'] !== null) {
        $(this).parent().append('<p id="titleDescription">'+ title['description'] +'</p>');
    }

    if ('prevede_esame' in title && title['prevede_esame'] !== null) {
        if (title['prevede_esame'] === false) {
            alert("Per i corsi che non prevedono esame, si prega di indicare la data e l'orario dell'ultima lezione del corso");
        }
    }
});

// Bottoni colorati sul click mostrare alert
$('.course-panels div').on('click', function(){
    if ($(this).hasClass('attivazione')) {
           $('.attivazionePanelWithForm').slideToggle();
        return;
    }
    alert('Il corso non è ancora creato.');
});
