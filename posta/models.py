"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
import logging
from smtplib import SMTPException, SMTPRecipientsRefused, SMTPResponseException, SMTPAuthenticationError

from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction, DatabaseError
from django.utils.html import strip_tags
from lxml import html

from base.models import *
from base.tratti import *
from social.models import ConGiudizio

logger = logging.getLogger('posta')


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConAllegati):

    logging = getattr(settings, 'POSTA_LOG_DEBUG', False)

    SUPPORTO_EMAIL = 'supporto@gaia.cri.it'
    SUPPORTO_NOME = 'Supporto Gaia'
    NOREPLY_EMAIL = 'noreply@gaia.cri.it'

    class Meta:
        verbose_name = "Messaggio di posta"
        verbose_name_plural = "Messaggi di posta"
        permissions = (
            ("view_messaggio", "Can view messaggio"),
        )

    LUNGHEZZA_MASSIMA_OGGETTO = 256
    CARATTERI_RIDUZIONE_OGGETTTO = '...'

    # Limite oggetto dato da RFC 2822 e' 998 caratteri in oggetto, ma ridotto per comodita
    oggetto = models.CharField(max_length=LUNGHEZZA_MASSIMA_OGGETTO, db_index=True,
                               blank=False, default="(Nessun oggetto)")
    corpo = models.TextField(blank=True, null=False, default="(Nessun corpo)")

    ultimo_tentativo = models.DateTimeField(blank=True, null=True, default=None)
    terminato = models.DateTimeField(blank=True, null=True, default=None)

    # Il mittente e' una persona o None (il sistema di Gaia)
    mittente = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True, on_delete=models.CASCADE)
    rispondi_a = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True,
                                   related_name="messaggi_come_rispondi_a", on_delete=models.CASCADE)

    # Flag per i messaggi cancellati (perche' obsoleti)
    eliminato = models.BooleanField(default=False, null=False)

    priorita = models.IntegerField(default=0, help_text="La priorità viene utilizzata per stabilire "
                                                        "l'ordine nello smistamento della coda, quando "
                                                        "c'è un errore questo valore viene incrementato")
    utenza = models.BooleanField(default=False, help_text="Se l'utente possiede un'email differente da quella "
                                                          "utilizzata per il login, il messaggio viene recapito ad "
                                                          "entrambe")

    @property
    def destinatari(self):
        """
        Ritorna la lista di tutti gli oggetti Persona destinatari di questo messaggio.
        :return:
        """
        from anagrafica.models import Persona
        return Persona.objects.filter(oggetti_sono_destinatario__messaggio=self)

    def destinatario(self, persona):
        """
        Controlla se la persona e' tra i destinatari.
        :param persona:
        :return:
        """
        return self.oggetti_destinatario.filter(persona=persona).exists()

    def primi_oggetti_destinatario(self):
        return self.oggetti_destinatario.all()[:50]

    @property
    def corpo_body(self):
        """
        Prova ad estrarre il corpo della pagina (body).
        :return:
        """
        if not self.corpo:
            return ""
        doc = html.document_fromstring(self.corpo)
        body = doc.xpath('//body')[0]
        body.tag = 'div'
        #try:
        return html.tostring(body)
        #except:
        #    return self.corpo
        #print html.parse('http://someurl.at.domain').xpath('//body')[0].text_content()

    def processa_link(self):
        """
        Controlla i link nella e-mail relativi e li rende assoluti.
        """
        doc = html.document_fromstring(self.corpo)
        links = doc.xpath('//a')
        for el in links:
            try:
                url = el.attrib['href']
                if '://' not in url:
                    el.attrib['href'] = "https://gaia.cri.it%s" % (url,)
            except KeyError:
                continue
        self.corpo = html.tostring(doc, pretty_print=True).decode('UTF-8')

    def accoda(self):
        """
        Salva e accoda il messaggio per l'invio asincrono.
        :return:
        """
        pass

    def allegati_pronti(self):
        return ()

    def log(self, *args, **kwargs):
        if self.logging:
            logger.debug(*args, **kwargs)

    @staticmethod
    def get_email_batch(limit=None):
        with transaction.atomic():
            # purtroppo skip_locked è stata inserita solo dalla version 1.11
            query = '''SELECT id FROM posta_messaggio WHERE terminato is NULL ORDER BY priorita'''
            if limit is not None:
                query += ' LIMIT %s'
                limit = (limit,)
            query += ' FOR UPDATE SKIP LOCKED'
            return [msg.pk for msg in Messaggio.objects.raw(query, limit)]

    @staticmethod
    @transaction.atomic()
    def invia(pk):
        results = []
        try:
            messaggio = Messaggio.objects.select_for_update(nowait=True).get(pk=pk, terminato__isnull=True)
        except (Messaggio.DoesNotExist, DatabaseError):  # DatabaseError se è locked, quindi in invio
            return ['OK: Riga lockata nel db']

        nome_mittente = messaggio.mittente.nome_completo if messaggio.mittente else Messaggio.SUPPORTO_NOME

        if messaggio.rispondi_a:
            if not messaggio.mittente:
                nome_mittente = messaggio.rispondi_a.nome_completo
            reply_to = ['{} <{}>'.format(messaggio.rispondi_a.nome_completo, messaggio.rispondi_a.email)]
        else:
            reply_to = None

        mittente = '{} <{}>'.format(nome_mittente, Messaggio.NOREPLY_EMAIL)
        plain_text = strip_tags(messaggio.corpo)

        connection = get_connection()
        messaggio.ultimo_tentativo = datetime.now()

        # non metto filter su inviato altrimenti non posso distiguere quelle senza destinatari
        destinatari = messaggio.oggetti_destinatario.all()

        for d in destinatari:
            if d.inviato:
                continue

            mail_to = [d.persona.email or Messaggio.SUPPORTO_EMAIL]
            if messaggio.utenza:
                email_utenza = getattr(getattr(d.persona, 'utenza', {}), 'email', None)
                if email_utenza != d.persona.email:
                    mail_to.append(email_utenza)

            msg = EmailMultiAlternatives(
                subject=messaggio.oggetto,
                body=plain_text,
                from_email=mittente,
                reply_to=reply_to,
                to=mail_to,
                attachments=messaggio.allegati_pronti(),
                connection=connection)
            msg.attach_alternative(messaggio.corpo, 'text/html')
            mail_to = ','.join(mail_to)
            try:
                # messaggio.log('Invio email a {}'.format(mail_to))
                msg.send()
            except SMTPRecipientsRefused as e:
                messaggio.log('Destinatari rifiutati {}: {}'.format(mail_to, e))
                d.errore = str(e)
                d.invalido = d.inviato = True
                messaggio.terminato = messaggio.ultimo_tentativo
                results.append('FAIL: Destinatari rifiutati {} - {}'.format(mail_to, e))
            except SMTPResponseException as e:
                messaggio.log('Errore invio email ai destinatari {}: {}'.format(mail_to, e))
                d.errore = str(e)
                if not isinstance(e, SMTPAuthenticationError) and ((e.smtp_code // 100) == 5):
                    d.invalido = d.inviato = True
                    messaggio.terminato = messaggio.ultimo_tentativo
                else:
                    messaggio.priorita += 1     # aumento priorità così verrà rischedulato dopo
                results.append('FAIL: {} - {}'.format(mail_to, e))
            except SMTPException as e:
                messaggio.log('Errore generico invio email {}: {}'.format(mail_to, e))
                d.errore = str(e)
                results.append('FAIL: SMTPException {} - {}'.format(mail_to, e))
            else:
                d.inviato = True
                d.errore = None
                results.append('OK: {} - Email inviata correttamente'.format(mail_to))
            finally:
                d.tentativo = messaggio.ultimo_tentativo
                d.save()

        if len(destinatari) == 0:
            msg = EmailMultiAlternatives(
                subject=messaggio.oggetto,
                body=plain_text,
                from_email=mittente,
                reply_to=reply_to,
                to=[Messaggio.SUPPORTO_EMAIL],
                attachments=messaggio.allegati_pronti(),
                connection=connection)
            msg.attach_alternative(messaggio.corpo, 'text/html')
            try:
                msg.send()
            except SMTPException as e:
                messaggio.log('Errore invio email a indirizzo del supporto: {}'.format(e))
                return ['FAIL: Invio a supporto - {}'.format(e)]
            else:
                # messaggio.log('Inviata email a indirizzo del supporto {}'.format(Messaggio.SUPPORTO_EMAIL))
                messaggio.terminato = messaggio.ultimo_tentativo
                return ['OK: Inviata a supporto']
            finally:
                messaggio.save()

        if not messaggio.oggetti_destinatario.filter(inviato=False):
            messaggio.terminato = messaggio.ultimo_tentativo
        messaggio.save()
        return results

    @classmethod
    def in_coda(cls):
        return cls.objects.filter(terminato=None).order_by('ultima_modifica')

    @classmethod
    def invia_raw(cls, oggetto, corpo_html, email_mittente,
                  reply_to=None, lista_email_destinatari=None,
                  allegati=None, fallisci_silenziosamente=False,
                  **kwargs):
        """
        Questo metodo puo' essere usato per inviare una e-mail
         immediatamente.
        """

        plain_text = strip_tags(corpo_html)
        lista_reply_to = [reply_to] if reply_to else []
        lista_email_destinatari = lista_email_destinatari or []
        allegati = allegati or []

        msg = EmailMultiAlternatives(
            subject=oggetto,
            body=plain_text,
            from_email=email_mittente,
            reply_to=lista_reply_to,
            to=lista_email_destinatari,
            **kwargs
        )
        msg.attach_alternative(corpo_html, "text/html")
        for allegato in allegati:
            msg.attach_file(allegato.file.path)
        return msg.send(fail_silently=fallisci_silenziosamente)

    @staticmethod
    def smaltisci_coda(dimensione_massima=50):
        """
            Metodo usato solo in test, non chiamare direttamente in produzione
            la coda è gestita da celery
        :param dimensione_massima: numero di emails da smistare
        :return: None
        """
        from django.core import mail
        assert hasattr(mail, 'outbox'), 'Questo metodo è da utilzzare solo per unittest'
        for pk in Messaggio.get_email_batch(dimensione_massima):
            Messaggio.invia(pk)

    @staticmethod
    def costruisci_e_accoda(oggetto='Nessun oggetto', modello='email_vuoto.html', corpo=None, mittente=None,
                            destinatari=None, allegati=None, **kwargs):
        """
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio
        """

        from .tasks import crea_email
        destinatari = destinatari or []
        destinatari = set([d.pk for d in destinatari])
        allegati = allegati or []
        allegati = set([a.pk for a in allegati])
        mittente = mittente.pk if mittente else None

        return crea_email(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente, destinatari=destinatari,
                          allegati=allegati, **kwargs)

    @staticmethod
    def costruisci_e_invia(oggetto=None, modello=None, corpo=None, mittente=None, destinatari=None, allegati=None,
                           **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo immediatamente.
         IMPORTANTE. Non adatto per messaggi con molti destinatari. In caso di fallimento immediato, il messaggio
                     viene accodato per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio inviato.
        """

        with transaction.atomic():
            msg = Messaggio.costruisci_e_accoda(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente,
                                                destinatari=destinatari, allegati=allegati, **kwargs)
            Messaggio.invia(msg.pk)
            return msg

    def __str__(self):
        return self.oggetto


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"
        permissions = (
            ("view_destinatario", "Can view destinatario"),
        )

    messaggio = models.ForeignKey(Messaggio, null=False, blank=True, related_name='oggetti_destinatario',
                                  on_delete=models.CASCADE)
    persona = models.ForeignKey("anagrafica.Persona", null=True, blank=True, default=None,
                                related_name='oggetti_sono_destinatario', on_delete=models.CASCADE)

    inviato = models.BooleanField(default=False, db_index=True)
    invalido = models.BooleanField(default=False, db_index=True)
    tentativo = models.DateTimeField(default=None, blank=True, null=True, db_index=True)
    errore = models.CharField(max_length=2048, blank=True, null=True, default=None, db_index=True)
