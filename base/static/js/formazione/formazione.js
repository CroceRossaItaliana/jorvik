// Parent template: formazione_corsi_base_nuovo.html

$('#formazioneCorsoNuovoForm').trigger("reset");

// Select: Tipo -> Show "Tipo del Corso" field
var titolo_form_group = $('#id_titolo_cri').closest('.form-group');
var level_form_group = $('#id_level').closest('.form-group');
var area_form_group = $('#id_area').closest('.form-group');
var course_value = 'C1';
var titolo_options_ajax_data = {};


function showDeliberaFileLink(value="") {
    if (!value) return;

    let delibera_label = $('label[for="id_delibera_file"]');
    let delibera_file_url = "";

    if (value === "1") delibera_file_url = "1";
    else if (value === "2") delibera_file_url = "2";
    else if (value === "3") delibera_file_url = "3";
    else if (value === "4") delibera_file_url = "4";
    else if (value === "firstAvailable") delibera_file_url = $('#id_level option:first').val();

    if (!delibera_file_url) return;

    let delibera_file_link = $('#delibera_file_link');
    if (delibera_file_link.length) delibera_file_link.remove();

    delibera_label.append("<div id='delibera_file_link'><a href='"+delibera_file_url+"' target='_blank'>Scarica delibera</a></div>");
}


if ($('#id_tipo option:selected').val() != course_value) {
    titolo_form_group.hide();
    level_form_group.hide();
    area_form_group.hide();
}

$('#id_tipo').on('change', function(e){
    let value = $(this).find('option:selected').val();
    if (value && value == course_value) {
        level_form_group.show();
        area_form_group.show();
        showDeliberaFileLink("firstAvailable");
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
    let value = $(this).val();

    // Reset area's selected option and hide its section
    $('#id_area').prop('selectedIndex',0);
    titolo_form_group.hide();

    if (value) {
        area_form_group.show();
        showDeliberaFileLink(value);
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
});

// Bottoni colorati sul click mostrare alert
$('.course-panels div').on('click', function(){
    if ($(this).hasClass('attivazione')) {
           $('.attivazionePanelWithForm').slideToggle();
        return;
    }
    alert('Il corso non è ancora creato.');
});
