from django import forms
from django.forms import Textarea
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries

from nocaptcha_recaptcha.fields import NoReCaptchaField


class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')
    captcha = NoReCaptchaField()



class ModuloMotivoNegazione(forms.Form):
    motivo = forms.CharField(label='Motivo negazione',
                             help_text="Fornisci una breve motivazione per la negazione di questa richiesta. "
                                       "Questa verrà comunicata al richiedente.",
                             required=True)


class ModuloLocalizzatore(forms.Form):
    indirizzo = forms.CharField(label='Indirizzo', required=False, help_text="es. Via Rosmini, 42. (Opzionale)")
    comune = forms.CharField(help_text="es. Cinisello Balsamo.")
    provincia = forms.CharField(required=True, min_length=3, help_text="es. Milano. (per intero)")
    stato = LazyTypedChoiceField(choices=countries, initial="IT")


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

    oggetto = forms.CharField(help_text="Una breve descrizione del problema, comprensiva del codice fiscale del volontario per cui richiedi assistenza.")
    descrizione = forms.CharField(widget=Textarea)
