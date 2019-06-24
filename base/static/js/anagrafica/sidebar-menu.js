function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).ajaxComplete(function() {
  var widget = document.createElement('script');
  widget.setAttribute('src', static_jorvik_js);
  widget.setAttribute('async', 'async');
  document.body.appendChild(widget);
});

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// ***
// Le variabili sono impostate in:
// - attivita_vuota.html, anagrafica_utente_vuota.html, ... (ogni template base dove viene chiamato il menu)
// - base/templates/base_vuota.html(csrf e view name)
// ***
$.ajax({
    type: "POST",
    url: url_get_async_sidebar_for_user,
    data: {
        csrf_token: csrftoken,
        section: section_name,
    },
    success: function(data) {
        $('#rightSidebarUtente').html(data.menu);
    },
    error: function(jqXHR, textStatus) {
        // console.log(jqXHR);
    }
});
