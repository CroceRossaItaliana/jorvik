import os
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from safedelete import safedelete_mixin_factory, SOFT_DELETE
from mptt.models import MPTTModel, TreeForeignKey
from anagrafica.permessi.applicazioni import PERMESSI_NOMI
from anagrafica.permessi.costanti import DELEGHE_OGGETTI_DICT
from base.notifiche import NOTIFICA_NON_INVIARE
from base.stringhe import GeneratoreNomeFile
from base.tratti import ConMarcaTemporale
from datetime import datetime

class ModelloSemplice(models.Model):
    """
    Questa classe astratta rappresenta un Modello generico.
    """

    class Meta:
        abstract = True


# Policy di cancellazioen morbida impostata su SOFT_DELETE
PolicyCancellazioneMorbida = safedelete_mixin_factory(SOFT_DELETE)


class ModelloCancellabile(ModelloSemplice, PolicyCancellazioneMorbida):
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


class ModelloAlbero(MPTTModel, ModelloSemplice):
    """
    Rappresenta un modello parte di un albero gerarchico.
    Nota bene: Per motivi tecnici, questo aggiunge anche un NOME.
    """

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ['nome']
        parent_attr = 'genitore'

    nome = models.CharField(max_length=64, unique=False, db_index=True)
    genitore = TreeForeignKey('self', null=True, blank=True, related_name='figli')

    def ottieni_superiori(self, includimi=False):
        return self.get_ancestors(include_self=includimi)

    def ottieni_figli(self):
        return self.get_children()

    def ottieni_discendenti(self, includimi=False):
        return self.get_descendants(include_self=includimi)

    def ottieni_fratelli(self, includimi=False):
        return self.get_siblings(include_self=includimi)

    def ottieni_numero_figli(self, includimi=False):
        n = self.get_descendant_count()
        if includimi:
            n += 1
        return n

    def figlio_di(self, altro, includimi=True):
        return self.is_descendant_of(altro, include_self=includimi)


class Autorizzazione(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta una richiesta di autorizzazione relativa ad un oggetto generico.
    Utilizzare tramite il tratto ConAutorizzazioni ed i suoi metodi.
    """

    class Meta:
        verbose_name_plural = "Autorizzazioni"
        app_label = "base"
        abstract = False

    richiedente = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="autorizzazioni_richieste")
    firmatario = models.ForeignKey("anagrafica.Persona", db_index=True, blank=True, null=True, default=None,
                                   related_name="autorizzazioni_firmate")
    concessa = models.NullBooleanField("Esito", db_index=True, blank=True, null=True, default=None)
    motivo_obbligatorio = models.BooleanField("Obbliga a fornire un motivo", default=False)
    motivo_negazione = models.CharField(blank=True, null=True, max_length=256)

    oggetto_tipo = models.ForeignKey(ContentType, db_index=True, related_name="autcomeoggetto")
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')

    necessaria = models.BooleanField("Necessaria", db_index=True, default=True)
    progressivo = models.PositiveSmallIntegerField("Progressivo contesto", default=1)

    destinatario_ruolo = models.CharField(max_length=2, choices=PERMESSI_NOMI)
    destinatario_oggetto_tipo = models.ForeignKey(ContentType, db_index=True, related_name="autcomedestinatari")
    destinatario_oggetto_id = models.PositiveIntegerField(db_index=True)
    destinatario_oggetto = GenericForeignKey('destinatario_oggetto_tipo', 'destinatario_oggetto_id')

    def firma(self, firmatario, concedi=True, modulo=None, motivo=None):
        """
        Firma l'autorizzazione.
        :param firmatario: Il firmatario.
        :param concedi: L'esito, vero per concedere, falso per negare.
        :param modulo: Se modulo necessario, un modulo valido.
        :return:
        """
        # Controlla che il modulo fornito, se presente, sia valido
        if modulo and not modulo.is_valid():
            raise ValueError("Il modulo richiesto per l'accettazione non e' stato completato correttamente.")

        self.concessa = concedi
        self.firmatario = firmatario
        self.necessaria = False
        self.save()

        # Se ha negato, allora avvisa subito della negazione.
        # Nessuna altra firma e' piu' necessaria.
        if not concedi:
            self.oggetto.confermata = False
            if self.motivo_obbligatorio:
                if not motivo:
                    raise ValueError("Non e' stato fornita una motivazione valida.")
                self.motivo_negazione = motivo
                self.save()
            self.oggetto.save()
            self.oggetto.autorizzazione_negata(motivo=motivo)
            self.oggetto.autorizzazioni_set().update(necessaria=False)
            if self.oggetto.INVIA_NOTIFICA_NEGATA:
                self.notifica_negata()
            return

        # Questa concessa, di questo progressivo non e' piu' necessaria
        # alcuna auutorizzazione.
        self.oggetto.autorizzazioni_set().filter(progressivo=self.progressivo).update(necessaria=False)

        # Se questa autorizzazione e' concessa, ed e' l'ultima.
        if self.oggetto.autorizzazioni_set().filter(necessaria=True).count() == 0:
            self.oggetto.confermata = True
            self.oggetto.save()
            self.oggetto.autorizzazione_concessa(modulo=modulo)
            if self.oggetto.INVIA_NOTIFICA_CONCESSA:
                self.notifica_concessa()

    def concedi(self, firmatario, modulo=None):
        self.firma(firmatario, True, modulo=modulo)

    def nega(self, firmatario, motivo=None):
        self.firma(firmatario, False, motivo=motivo)

    @property
    def template_path(self):
        """
        Ritorna il nome del template dell'autorizzazione.
        """
        return 'base_autorizzazioni_inc_%s_%s.html' % (
            self.oggetto._meta.app_label.lower(),
            self.oggetto._meta.object_name.lower()
        )

    def notifica_richiesta(self):
        from anagrafica.models import Delega, Persona
        from posta.models import Messaggio

        tipo = ContentType.objects.get_for_model(self.destinatario_oggetto)
        destinatari = [d.persona for d in
                       Delega.query_attuale().filter(tipo=self.destinatario_ruolo,
                                                     oggetto_tipo__pk=tipo.pk,
                                                     oggetto_id=self.destinatario_oggetto.pk)]
        if not destinatari:
            return  # Nessun destinatario, nessuna e-mail.
        Messaggio.costruisci_e_invia(
            oggetto="Richiesta di %s da %s" % (self.oggetto.RICHIESTA_NOME, self.richiedente.nome_completo,),
            modello="email_autorizzazione_richiesta.html",
            corpo={
                "richiesta": self,
            },
            mittente=self.richiedente,
            destinatari=destinatari,
        )

    def notifica_concessa(self):
        from posta.models import Messaggio
        Messaggio.costruisci_e_invia(
            oggetto="Richiesta di %s APPROVATA" % (self.oggetto.RICHIESTA_NOME,),
            modello="email_autorizzazione_concessa.html",
            corpo={
                "richiesta": self,
            },
            mittente=self.firmatario,
            destinatari=[self.richiedente]
        )

    def notifica_negata(self):
        from posta.models import Messaggio
        Messaggio.costruisci_e_invia(
            oggetto="Richiesta di %s RESPINTA" % (self.oggetto.RICHIESTA_NOME,),
            modello="email_autorizzazione_negata.html",
            corpo={
                "richiesta": self,
            },
            mittente=self.firmatario,
            destinatari=[self.richiedente]
        )



class ConAutorizzazioni(models.Model):
    """
    Aggiunge la possibilita' di aggiungere le funzionalita'
    di autorizzazione ad un ogetto.
    """

    class Meta:
        abstract = True

    autorizzazioni = GenericRelation(
        Autorizzazione,
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    confermata = models.BooleanField("Confermata", default=True, db_index=True)
    ritirata = models.BooleanField("Ritirata", default=False, db_index=True)

    ESITO_OK = "Confermato"
    ESITO_NO = "Negato"
    ESITO_RITIRATA = "Ritirata"
    ESITO_PENDING = "In attesa"

    # Sovrascrivimi! Invia notifiche e-mail?
    INVIA_NOTIFICHE = True

    INVIA_NOTIFICA_CONCESSA = INVIA_NOTIFICHE
    INVIA_NOTIFICA_NEGATA = INVIA_NOTIFICHE

    # Sovrascrivimi!
    RICHIESTA_NOME = "autorizzazione"

    @classmethod
    def con_esito(cls, esito):
        """
        Ottiene QuerySet degli oggetti con esito selezionato.
        :param esito: L'esito: (*ConAutorizzazioni.ESITO_OK, .ESITO_NO, .ESITO_PENDING, .ESITO_RITIRATA).
        :return: QuerySet filtrato.
        """
        if esito == cls.ESITO_OK:
            return cls.objects.filter(confermata=True, ritirata=False)

        elif esito == cls.ESITO_RITIRATA:
            return cls.objects.filter(ritirata=True)

        elif esito == cls.ESITO_PENDING:
            # Confermata = False, ma almeno una autorizzazione e nessuna negata
            tipo = ContentType.objects.get_for_model(cls)
            return cls.objects.filter(confermata=False, ritirata=False,
                  pk__in=Autorizzazione.objects.filter(oggetto_tipo__pk=tipo.id).values_list('oggetto_id', flat=True))\
                .exclude(
                  pk__in=Autorizzazione.objects.filter(oggetto_tipo__pk=tipo.id, concessa=False).values_list('oggetto_id', flat=True)
            )

        else:  # ESITO_NO
            tipo = ContentType.objects.get_for_model(cls)
            return cls.objects.filter(
                # Confermata = False, ma non pendente
                confermata=False,
            ).exclude(pk__in=cls.con_esito(cls.ESITO_PENDING))

    @classmethod
    def con_esito_ok(cls):
        """
        Ottiene un QuerySet per tutti gli oggetti con esito ESITO_OK.
        :return:
        """
        return cls.con_esito(cls.ESITO_OK)

    @classmethod
    def con_esito_ritirata(cls):
        """
        Ottiene un QuerySet per tutti gli oggetti con esito ESITO_RITIRATA.
        :return:
        """
        return cls.con_esito(cls.ESITO_RITIRATA)

    @classmethod
    def con_esito_pending(cls):
        """
        Ottiene un QuerySet per tutti gli oggetti con esito ESITO_PENDING.
        :return:
        """
        return cls.con_esito(cls.ESITO_PENDING)

    @classmethod
    def con_esito_no(cls):
        """
        Ottiene un QuerySet per tutti gli oggetti con esito ESITO_NO.
        :return:
        """
        return cls.con_esito(cls.ESITO_NO)

    @property
    def esito(self):
        """
        Ottiene l'esito. (*ConAutorizzazioni.ESITO_OK, .ESITO_NO, .ESITO_PENDING, .ESITO_RITIRATA).
        :return:
        """
        if self.confermata:  # Se confermata, okay
            return self.ESITO_OK

        elif self.ritirata:  # Ritirata?
            return self.ESITO_RITIRATA

        elif self.autorizzazioni.filter(concessa=False).exists():  # Altrimenti, se almeno una negazione, esito negativo
            return self.ESITO_NO

        elif not self.autorizzazioni.exists():  # Se non vi e' nessuna richiesta, allora e' negata d'ufficio
            return self.ESITO_NO

        else:  # Se non confermata e nessun esito negativo, ancora pendente
            return self.ESITO_PENDING

    @property
    def autorizzazioni_negate(self):
        return self.autorizzazioni.filter(concessa=False)

    @property
    def autorizzazioni(self):
        return self.autorizzazioni_set()

    def autorizzazioni_set(self):
        """
        Ottiene il queryset delle autorizzazioni associate.
        :return: Queryset.
        """
        tipo = ContentType.objects.get_for_model(self)
        return Autorizzazione.objects.filter(oggetto_tipo__pk=tipo.id, oggetto_id=self.id)

    def autorizzazione_richiedi(self, richiedente, destinatario, motivo_obbligatorio=True, **kwargs):
        """
        Richiede una autorizzazione per l'oggetto attuale

        :param richiedente: Colui che inoltra la richiesta.
        :param destinatario: Il ruolo che deve firmare l'autorizzazione, in forma
                      (RUOLO, OGGETTO). Puo' anche essere tupla ((Ruolo1, Ogg1), (Ruolo2, Ogg2), ...)
        :param motivo_obbligatorio: Vero se si vuole forzare l'inserimento della motivazione in caso di rifiuto.
        :param kwargs:
        :return:
        """

        try:  # Cerca l'autorizzazione per questo oggetto con progressivo maggiore
            ultima = self.autorizzazioni_set().latest('progressivo')
            # Se esiste, calcola il prossimo progressivo per l'oggetto
            prossimo_progressivo = ultima.progressivo + 1

        except ObjectDoesNotExist:  # Se non esiste, ricomincia
            prossimo_progressivo = 1

        # Mi aspetto piu' destinatari. Se solo uno,
        # lo rendo tupla cosi' da poterci comunque ciclare.
        if type(destinatario[0]) is not tuple:
            destinatario = (destinatario, )

        # Per ogni destinatario aspettato
        for i in destinatario:

            # Policy se non specificata
            notifica_invia = NOTIFICA_NON_INVIARE

            try:  # Controlla se la policy e' specificata
                (ruolo, oggetto, notifica_invia) = i

            except ValueError:  # Altrimenti, estrai comunque ruolo e oggetto
                (ruolo, oggetto) = i

            if ruolo not in DELEGHE_OGGETTI_DICT:
                raise ValueError("Il ruolo che si richiede firmi questa autorizzazione non esiste.")

            if oggetto.__class__.__name__ != DELEGHE_OGGETTI_DICT[ruolo]:
                raise ValueError("L'oggetto specificato non e' valido per il ruolo che si richiede firmi "
                                 "l'autorizzazione.")

            r = Autorizzazione(
                richiedente=richiedente,
                destinatario_ruolo=ruolo,
                destinatario_oggetto=oggetto,
                progressivo=prossimo_progressivo,
                oggetto=self,
                motivo_obbligatorio=motivo_obbligatorio,
                **kwargs
            )
            r.save()

            if notifica_invia:
                r.notifica_richiesta()

        # Rimuovi eventuale stato di confermata
        self.confermata = False
        self.save()

        # Evita cache per esito
        self.refresh_from_db()

    def autorizzazioni_ritira(self):
        """
        Ritira le autorizzazioni pendenti ed imposta lo stato a ritirato.
        :return:
        """
        self.ritirata = True

        # Non diventa piu' necessaria alcuna autorizzazione tra quelle richieste
        self.autorizzazioni.update(necessaria=False)

    def autorizzazione_concessa(self, modulo=None):
        """
        Sovrascrivimi! Ascoltatore per concessione autorizzazione.
        """
        pass

    def autorizzazione_negata(self, motivo=None):
        """
        Sovrascrivimi! Ascoltatore per negazione autorizzazione.
        """
        pass

    def autorizzazione_concedi_modulo(self):
        """
        Sovrascrivimi! Ritorna la classe del modulo per la conferma.
        """
        return None


class ConScadenza:
    """
    Aggiunge un attributo DateTimeField scadenza.
    """

    class Meta:
        abstract = True

    scadenza = models.DateTimeField("Scadenza", null=True, blank=True, db_index=True, default=None)

    @property
    def scaduto(self):
        """
        Controlla se l'oggetto e' gia' scaduto o meno.

        :return:
        """
        if not self.scadenza:
            return False
        return self.scadenza < datetime.now()

    @classmethod
    def scaduti(cls):
        """
        Ottiene il queryset di oggetti scaduti (per la cancellazione?)
        :return:
        """
        return cls.objects.exclude(scadenza__isnull=True).filter(scadenza__lte=datetime.now())

    @classmethod
    def pulisci(cls):
        """
        Cancella gli elementi scaduti.
        :return: Il numero di elementi cancellati.
        """
        n = cls.scaduti().count()
        cls.scaduti().delete()
        return n


class Token(ModelloSemplice, ConMarcaTemporale):
    pass


class Allegato(ConMarcaTemporale, ConScadenza, ModelloSemplice):
    """
    Rappresenta un allegato generico in database, con potenziale scadenza.
    """

    class Meta:
        verbose_name_plural = "Allegati"

    oggetto_tipo = models.ForeignKey(ContentType, db_index=True, blank=True, null=True, related_name="allegato_come_oggetto")
    oggetto_id = models.PositiveIntegerField(db_index=True, blank=True, null=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')
    file = models.FileField("File", upload_to=GeneratoreNomeFile('allegati/'))
    nome = models.CharField("Nome file", max_length=64, default="File", blank=False, null=False)

    @property
    def download_url(self):
        """
        Ritorna l'URL per il download del file.
        """
        return self.file.url

    def prepara_cartelle(self, file_path, path_include_file=True):
        """
        Crea ricorsivamente le directory per la creazione di un file.
        Se path_include_file non specificato o True, il primo parametro aspettato e' il path completo
        al nuovo file. Altrimenti, solo il percorso da creare e' aspettato.
        """
        if path_include_file:
            path = os.path.dirname(file_path)
        else:
            path = file_path

        if os.path.isdir(path):
            return True

        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == 17:
                # Dir already exists. No biggie.
                pass

        return True


class ConAllegati(models.Model):
    """
    Aggiunge la possibilita' di allegare file all'oggetto, anche con scadenza.
    """

    allegati = GenericRelation(
        Allegato,
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    class Meta:
        abstract = True
