// membri nascosti
let tipo_partnership = $('#id_titoli_in_partnership');
let tipo_titoli_altri = $('#id_altri_titolo');
let argomenti = $('#id_argomento');
let no_corso = $('#id_no_corso');
let no_argomento = $('#id_no_argomento');
let nome_corso = $('#id_nome_corso');
let argomento_nome = $('#id_argomento_nome');

let tipo_partnership_blocco = tipo_partnership.parent();
let tipo_titoli_altri_blocco = tipo_titoli_altri.parent().parent();
let argomenti_blocco = argomenti.parent();
let no_corso_blocco = no_corso.parent();
let no_argomento_blocco = no_argomento.parent();
let nome_corso_blocco = nome_corso.parent();
let argomento_nome_blocco = argomento_nome.parent();

tipo_partnership_blocco.hide();
tipo_titoli_altri_blocco.hide();
argomenti_blocco.hide();
no_corso_blocco.hide();
nome_corso_blocco.hide();
argomento_nome_blocco.hide();
no_argomento_blocco.hide();

let tipo_titolo = $('#id_tipo_altro_titolo');

tipo_titolo.change(function () {
    let select_val = $(this).val();
    if (select_val === 'PT') {
        tipo_partnership_blocco.show();
        tipo_titoli_altri_blocco.hide();
        argomenti_blocco.hide();
        no_corso_blocco.hide();
        nome_corso_blocco.hide();
        argomento_nome_blocco.hide();
        no_argomento_blocco.hide();
    } else if (select_val === 'AL') {
        tipo_partnership_blocco.hide();
        tipo_titoli_altri_blocco.show();
        argomenti_blocco.hide();
        no_corso_blocco.show();
        nome_corso_blocco.hide();
        argomento_nome_blocco.hide();
        no_argomento_blocco.hide();
    } else {
        tipo_partnership_blocco.hide();
        tipo_titoli_altri_blocco.hide();
        argomenti_blocco.hide();
        no_corso_blocco.hide();
        nome_corso_blocco.hide();
        argomento_nome_blocco.hide();
        no_argomento_blocco.hide();
    }
})

function popolaArgomenti(e) {
    let titolo_id = $(this).val();
    if (titolo_id !== '') {
        $.ajax({
            type: "POST",
            url: url_cv_cdf_titolo_json,
            data: {
                id: titolo_id,
                csrf_token: _csrf_token,
            },
            success: function (data) {
                argomenti.find('option').remove();
                $.each(data, function (id, text) {
                    argomenti.append($('<option>', {
                        value: id,
                        text: text,
                    }));
                });
                argomenti_blocco.show();
                no_argomento_blocco.show();
                return data;
            },
            error: function (jqXHR, textStatus) {
                <!--console.log(textStatus);-->
            },
        });

    } else {
        argomenti_blocco.hide();
        argomenti.find('option').remove();
    }
}

tipo_partnership.on('change', popolaArgomenti);
tipo_titoli_altri.on('change', popolaArgomenti);
no_corso.on('change', function (e) {
    if ($(this).is(':checked')) {
        tipo_titoli_altri_blocco.hide();
        nome_corso_blocco.show();
        argomento_nome_blocco.show();
        argomenti_blocco.hide();
        no_argomento_blocco.hide();
    } else {
        tipo_titoli_altri_blocco.show();
        nome_corso_blocco.hide();
        argomento_nome_blocco.hide();
        argomenti_blocco.hide();
        no_argomento_blocco.hide();
    }
});
no_argomento.on('change', function (e) {
    if ($(this).is(':checked')) {
        argomenti_blocco.hide()
        argomento_nome_blocco.show()
    } else {
        argomenti_blocco.show()
        argomento_nome_blocco.hide()
    }
});
nome_corso.keypress(function (e) {
    argomento_nome_blocco.show();
});
