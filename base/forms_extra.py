from django import forms
from django.forms import Textarea
from autocomplete_light import shortcuts as autocomplete_light


class ModuloRichiestaSupporto(forms.Form):

    PRIMO_LIVELLO = "INF"
    SECONDO_LIVELLO = "REQ"
    TERZO_LIVELLO = "INC"
    FEEDBACK = "FEE"
    SANGUE = "BLO"
    AREA_SVILUPPO = "SVI"
    TIPO = (
        (None, "-- Seleziona una opzione --"),
        (PRIMO_LIVELLO, "Informazione: Aiuto con l'utilizzo di Gaia"),
        (SECONDO_LIVELLO, "Richiesta: Modifica informazioni o correzioni"),
        (TERZO_LIVELLO, "Incidente: Errori o segnalazioni di sicurezza"),
        (AREA_SVILUPPO, "Area VI: Ripristino password e richieste e-mail istituzionali (@cri.it, PEC)"),
        (FEEDBACK, "Feedback GAIA (suggerimenti, critiche, idee)"),
        (SANGUE, "Feedback in merito alla donazione sangue"),

    )

    tipo = forms.ChoiceField(TIPO, required=True, initial=None,
                                   help_text="Seleziona una delle tipologie di richiesta "
                                             "per aiutarci a smistarla rapidamente.")

    oggetto = forms.CharField(help_text="Una breve descrizione del problema.")
    descrizione = forms.CharField(widget=Textarea)


class ModuloRichiestaSupportoPersone(ModuloRichiestaSupporto):
    persona = autocomplete_light.ModelChoiceField(
        "PersonaAutocompletamento", help_text="Seleziona la persona per cui si richiede assistenza."
                                              "Nel caso la problematica impattasse più persone è necessario "
                                              "aprire una segnalazione per ogni persona ",
        required=False
    )

    field_order = ('tipo', 'oggetto', 'persona', 'descrizione')