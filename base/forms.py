from django import forms
from django.forms import Textarea
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries


class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')


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

    PRIMO_LIVELLO = "LIV1"
    SECONDO_LIVELLO = "LIV2"
    TERZO_LIVELLO = "LIV3"
    FEEDBACK = "FEEDBACK"
    SANGUE = "SANGUE"
    TIPO = (
        (PRIMO_LIVELLO, "Aiuto con l'utilizzo di Gaia"),
        (SECONDO_LIVELLO, "Modifica informazioni o correzioni"),
        (TERZO_LIVELLO, "Errori o segnalazioni di sicurezza"),
        (FEEDBACK, "Feedback (suggerimenti, critiche, idee)"),
        (SANGUE, "Feedback in merito alla donazione sangue"),
    )

    tipo = forms.ChoiceField(TIPO, help_text="Seleziona una delle tipologie di richiesta "
                                             "per aiutarci a smistarla rapidamente.")

    oggetto = forms.CharField(help_text="Una breve descrizione del problema.")
    descrizione = forms.CharField(widget=Textarea)
