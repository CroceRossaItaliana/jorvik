from django import forms
from .models import Page


class ImportAndGenerateStaticPage(forms.Form):
    GLOSSARIO_CORSI = "glossario-corsi"
    CATALOGO_CORSI = "catalogo-corsi"
    TYPE_CHOICES = [
        (GLOSSARIO_CORSI, 'Glossario Corsi'),
        (CATALOGO_CORSI, 'Catalogo Corsi'),
    ]

    type = forms.ChoiceField(choices=TYPE_CHOICES)
    file = forms.FileField()
