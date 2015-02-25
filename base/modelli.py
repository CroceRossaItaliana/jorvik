from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from safedelete import safedelete_mixin_factory, SOFT_DELETE
from anagrafica.modelli import Persona
from base.tratti import ConMarcaTemporale
from mptt.models import MPTTModel, TreeForeignKey


class ModelloSemplice(models.Model):
    """
    Questa classe astratta rappresenta un Modello generico.
    """

    class Meta:
        abstract = True


# Policy di cancellazioen morbida impostata su SOFT_DELETE
PolicyCancellazioneMorbida = safedelete_mixin_factory(SOFT_DELETE)


class ModelloCancellabile(PolicyCancellazioneMorbida, ModelloSemplice):
    """
    Questa classe astratta rappresenta un Modello generico, con
    aggiunta la caratteristica di avere cancellazione SOFT DELETE.

    Un modello che estende questa classe, quando viene cancellato,
    viene invece mascherato e nascosto dalle query di ricerca.

    Tutte le entita' correlate vengono comunque mantenute. Risolvere
    un collegamento a questa entita' risultera' nell'ottenere questo
    oggetto, anche se cancellato.
    """

    class Meta:
        abstract = True


class ModelloAlbero(ModelloSemplice, MPTTModel):
    """
    Rappresenta un modello parte di un albero gerarchico.
    Nota bene: Per motivi tecnici, questo aggiunge anche un NOME.
    """

    class MPTTMeta:
        order_insertion_by = ['nome']

    nome = models.CharField(max_length=64, unique=False, db_index=True)
    genitore = TreeForeignKey('self', null=True, blank=True, related_name='figli')

    def ottieni_figli(self):
        return self.get_children()

    def ottieni_discendenti(self, includimi=True):
        return self.get_descendant_count(include_self=includimi)

    def ottieni_numero_figli(self, includimi=False):
        n = self.get_descendant_count()
        if includimi:
            n += 1
        return n


"""
Seguono qui le entita' di base.
- Giudizio
- Commento
- Autorizzazione
"""



class Giudizio(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un giudizio sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConGiudizio ed i suoi metodi.
    """
    autore = models.ForeignKey("Autore", Persona, db_index=True, related_name="giudizi")
    positivo = models.BooleanField("Positivo", db_index=True)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')


class Commento(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un commento sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConCommento ed i suoi metodi.
    """
    autore = models.ForeignKey("Autore", Persona, db_index=True, related_name="commenti")
    commento = models.TextField("Testo del commento")
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')


class Autorizzazione(ModelloSemplice, ConMarcaTemporale):
    richiedente = models.ForeignKey("Richiedente", Persona, db_index=True, related_name="autorizzazioni_richieste")
    destinatario = models.ForeignKey("Destinatario", Persona, db_index=True, related_name="autorizzazioni_destinate")
    firmatario = models.ForeignKey("Firmatario", Persona, db_index=True, blank=True, null=True, default=None, related_name="autorizzazioni_firmate")
    concessa = models.BooleanField("Esito", db_index=True, blank=True, null=True, default=None)
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

