import os

from django.apps import apps
from django.http import HttpResponse
from django.shortcuts import redirect

from anagrafica.permessi.costanti import ERRORE_PERMESSI, LETTURA
from base.tratti import ConPDF
from base.errori import errore_generico


class BaseGeneraPDF:
    def __init__(self, request, me, app_label, model, pk):
        self.request = request
        self.me = me
        self.app_label = app_label
        self.model = model
        self.pk = pk

    def make(self, **kwargs):
        oggetto = apps.get_model(self.app_label, self.model).objects.get(pk=self.pk)

        if not isinstance(oggetto, ConPDF):
            return errore_generico(self.request, None,
                messaggio="Impossibile generare un PDF per il tipo specificato.")

        if 'token' in self.request.GET:
            if not oggetto.token_valida(self.request.GET['token']):
                return errore_generico(self.request, self.me,
                                       titolo="Token scaduta",
                                       messaggio="Il link usato è scaduto.")

        elif not self.me.permessi_almeno(oggetto, LETTURA):
            if not self.me.is_presidente_regionale and not self.me.is_responsabile_formazione_regionale:
                return redirect(ERRORE_PERMESSI)

        pdf = oggetto.genera_pdf(self.request, **kwargs)

        # Se sto scaricando un tesserino, forza lo scaricamento.
        if 'tesserini' in pdf.file.path:
            return self.pdf_forza_scaricamento(pdf)

        return redirect(pdf.download_url)

    def pdf_forza_scaricamento(self, pdf):
        """
        Forza lo scaricamento di un file pdf.
        Da usare con cautela, perche' carica il file in memoria
        e blocca il thread fino al completamento della richiesta.
        :param request:
        :param pdf:
        :return:
        """

        from mimetypes import guess_type

        percorso_completo = pdf.file.path

        with open(percorso_completo, 'rb') as f:
            data = f.read()

        response = HttpResponse(data, content_type=guess_type(percorso_completo)[0])
        response['Content-Disposition'] = "attachment; filename=%s" % pdf.nome
        response['Content-Length'] = os.path.getsize(percorso_completo)
        return response
