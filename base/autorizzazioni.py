from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Autorizzazione(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta una richiesta di autorizzazione relativa ad un oggetto generico.
    Utilizzare tramite il tratto ConAutorizzazioni ed i suoi metodi.
    """

    class Meta:
        verbose_name = "Richiesta di autorizzazione"
        verbose_name_plural = "Richieste di autorizzazione"
        app_label = "base"

    richiedente = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="autorizzazioni_richieste")
    destinatario = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="autorizzazioni_destinate")
    firmatario = models.ForeignKey("anagrafica.Persona", db_index=True, blank=True, null=True, default=None, related_name="autorizzazioni_firmate")
    concessa = models.NullBooleanField("Esito", db_index=True, blank=True, null=True, default=None)
    motivo_obbligatorio = models.BooleanField("Obbliga a fornire un motivo", default=False)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')

    def firma(self, firmatario, concedi=True):
        """
        Firma l'autorizzazione.
        :param firmatario: Il firmatario.
        :param concedi: L'esito, vero per concedere, falso per negare.
        :return:
        """
        self.concessa = concedi
        self.firmatario = firmatario

        # Se ha negato, allora avvisa subito della negazione.
        if not concedi:
            self.oggetto.autorizzazione_negata()

        # Se questa autorizzazione e' concessa, ed e' l'ultima.
        elif self.oggetto.autorizzazioni.exclude(self).count() == 0:
            self.oggetto.autorizzazione_concessa()

    def concedi(self, firmatario):
        self.firma(firmatario, True)

    def nega(self, firmatario):
        self.firma(firmatario, False)


class ConAutorizzazioni():
    """
    Aggiunge la possibilita' di aggiungere le funzionalita'
    di autorizzazione ad un ogetto.
    """

    class Meta:
        abstract = True

    autorizzazioni = GenericRelation(
        "base.Autorizzazione",
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    def autorizzazione_richiedi(self, richiedente, destinatario, motivo_obbligatorio=False, **kwargs):
        """
        Richiede una autorizzazione per l'oggetto attuale
        :param richiedente: Colui che inoltra la richiesta.
        :param destinatario: Colui che si vuole che autorizzi.
        :param motivo_obbligatorio: Vero se si vuole forzare l'inserimento della motivazione in caso di rifiuto.
        :param kwargs:
        :return:
        """
        r = Autorizzazione(
            richiedente=richiedente,
            destinatario=destinatario,
            oggetto=self,
            motivo_obbligatorio=motivo_obbligatorio,
            **kwargs
        )
        r.save()

    def autorizzazione_concessa(self):
        """
        Sovrascrivimi! Ascoltatore per concessione autorizzazione.
        """
        pass

    def autorizzazione_negata(self, motivo=None):
        """
        Sovrascrivimi! Ascoltatore per negazione autorizzazione.
        """
        pass

    def autorizzazione_esito(self):
        """
        Restituisce l'esito delle richieste di autorizazzione.
        True per concessa, False per negata, None per pendente.
        """
        # Ci sono autorizzazioni negate?
        if self.autorizzazioni.filter(concessa=False).count():
            return False

        # Ci sono autorizzazioni pendenti?
        elif self.autorizazzioni.filter(concessa__isnull=True).count():
            return None

        # Sono tutte concesse.
        return True

    def autorizzazione_esito_in_testo(self):
        esito = self.autorizzazione_esito()
        if esito:
            return "Concessa"
        elif esito is None:
            return "In attesa"
        return "Negata"
