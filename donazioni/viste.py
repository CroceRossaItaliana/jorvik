from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA, ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata, VistaDecorata


class DonazioniWelcomePage(VistaDecorata, TemplateView):
    template_name = 'donazioni.html'

    @method_decorator(pagina_privata(permessi=[GESTIONE_CAMPAGNE]))
    def get(self, request, *args, **kwargs):
        try:
            return super(DonazioniWelcomePage, self).get(request, *args, **kwargs)
        except Http404:
            return redirect(ERRORE_PERMESSI)

    def get_context_data(self, **kwargs):
        contesto = super(DonazioniWelcomePage, self).get_context_data(**kwargs)
        me = contesto.get('me')
        contesto.update({
            "sedi": me.oggetti_permesso(GESTIONE_CAMPAGNE),
            "campagne": me.oggetti_permesso(GESTIONE_CAMPAGNA),
        })
        return contesto
