from django import forms

from gestione_file.models import DocumentoComitato


class ModuloAggiungiDocumentoComitato(forms.ModelForm):
    expires = forms.DateField(required=False, label='Data di scadenza (se previsto)')

    class Meta:
        model = DocumentoComitato
        fields = ['nome', 'file', 'expires', ]
