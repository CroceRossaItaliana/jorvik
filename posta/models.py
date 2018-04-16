"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
import logging
from smtplib import SMTPException, SMTPRecipientsRefused, SMTPResponseException, SMTPAuthenticationError

from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction, DatabaseError
from django.template.loader import get_template
from django.utils.html import strip_tags
from celery import uuid
from django.utils.text import Truncator
from lxml import html

from .tasks import invia_mail
from base.models import *
from base.tratti import *
from social.models import ConGiudizio

logger = logging.getLogger('posta')


class ErrorePosta(Exception):
    pass


class ErrorePostaTemporaneo(ErrorePosta):
    pass


class ErrorePostaFatale(ErrorePosta):
    pass


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

    utenza = models.BooleanField(default=False, help_text="Se l'utente possiede un'email differente da quella "
                                                          "utilizzata per il login, il messaggio viene recapito ad "
                                                          "entrambe")

    task_id = models.CharField(max_length=36, blank=True, null=True)

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
    def invia_no_lock(pk):
            try:
                messaggio = Messaggio.objects.select_for_update(nowait=True).get(pk=pk, terminato__isnull=True)
            except Messaggio.DoesNotExist:  # Messaggio già inviato
                return ['SKIP: Mesaggio già inviato']
            except DatabaseError:  # DatabaseError se è locked, quindi in invio
                return ['SKIP: Riga lockata nel db']

            if messaggio.mittente:
                nome_mittente = messaggio.mittente.nome_completo
                email_mittente = messaggio.mittente.email or Messaggio.NOREPLY_EMAIL
            else:
                nome_mittente = Messaggio.SUPPORTO_NOME
                email_mittente = Messaggio.SUPPORTO_EMAIL

            if messaggio.rispondi_a:  # Rispondi a definito?
                if not messaggio.mittente:  # Se si, e nessun mittente, usa nome mittente del reply-to
                    nome_mittente = messaggio.rispondi_a.nome_completo
                reply_to = ['{} <{}>'.format(messaggio.rispondi_a.nome_completo, messaggio.rispondi_a.email)]
            else:  # Altrimenti, imposta reply-to allo stesso mittente
                reply_to = ['{} <{}>'.format(nome_mittente, email_mittente)]

            mittente = '{} <{}>'.format(nome_mittente, Messaggio.NOREPLY_EMAIL)
            plain_text = strip_tags(messaggio.corpo)

            connection = get_connection()
            messaggio.ultimo_tentativo = datetime.now()

            # non metto filter su inviato altrimenti non posso distiguere quelle senza destinatari
            destinatari = list(messaggio.oggetti_destinatario.all())

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
                except (ConnectionError, SMTPException) as e:  # supponiamo che l'indirizzo del supporto sia corretto
                    messaggio.log('Errore invio email a indirizzo del supporto: {}'.format(e))
                    return ErrorePostaTemporaneo('Errore invio email a indirizzo del supporto')
                except Exception as e:
                    messaggio.log('Errore invio email a indirizzo del supporto: {}'.format(e))
                    messaggio.terminato = messaggio.ultimo_tentativo
                    messaggio.task_id = None
                    return ErrorePostaFatale('Errore imprevisto invio a indirizzo del supporto'.format(e))
                else:
                    # messaggio.log('Inviata email a indirizzo del supporto {}'.format(Messaggio.SUPPORTO_EMAIL))
                    messaggio.terminato = messaggio.ultimo_tentativo
                    messaggio.task_id = None
                    return ['OK: Inviata a supporto']
                finally:
                    messaggio.save()

            risultati = []
            for d in list(destinatari):
                if d.inviato:
                    destinatari.remove(d)
                    continue

                # Se la persona non ha un indirizzo di posta, segna questo oggetto Destinatario
                # come inviato e continua col prossimo Destinatario
                if not d.persona.email:
                    d.inviato = True
                    d.errore = 'Nessun indirizzo email'
                    risultati.append('OK: Persona id={} non ha email'.format(d.persona.pk))
                    d.save()
                    destinatari.remove(d)
                    continue

                mail_to = [d.persona.email]
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
                except ConnectionError as e:
                    messaggio.log('Errore di connessione al server di posta {}'.format(e))
                    messaggio.save()
                    return ErrorePostaTemporaneo('Errore di connessione al server di posta')  # occorre rifare connect
                except SMTPRecipientsRefused as e:
                    messaggio.log('Destinatari rifiutati {}: {}'.format(mail_to, e))
                    d.errore = str(e)
                    d.invalido = d.inviato = True
                    risultati.append('FAIL: Destinatari rifiutati {} - {}'.format(mail_to, e))
                except SMTPResponseException as e:
                    messaggio.log('Errore invio email ai destinatari {}: {}'.format(mail_to, e))
                    d.errore = str(e)
                    if not isinstance(e, SMTPAuthenticationError) and ((e.smtp_code // 100) == 5):
                        d.invalido = d.inviato = True
                        risultati.append('FAIL: {} - {}'.format(mail_to, e))
                        destinatari.remove(d)
                except SMTPException as e:
                    messaggio.log('Errore generico invio email {}: {}'.format(mail_to, e))
                    d.errore = str(e)
                    risultati.append('FAIL: SMTPException {} - {}'.format(mail_to, e))
                except Exception as e:
                    messaggio.log('Errore imprevisto invio email {}: {}'.format(mail_to, e))
                    d.errore = str(e)
                    d.invalido = d.inviato = True
                    risultati.append('FAIL: {} - Errore imprevisto {}'.format(mail_to, e))
                    destinatari.remove(d)
                else:
                    d.inviato = True
                    d.errore = None
                    risultati.append('OK: {} - Email inviata correttamente'.format(mail_to))
                    destinatari.remove(d)
                finally:
                    d.tentativo = messaggio.ultimo_tentativo
                    d.save()

            if destinatari:
                return ErrorePostaTemporaneo('Messaggio non inviato a tutti i destinatari')
            else:
                # messaggio.log('Inviata email a indirizzo del supporto {}'.format(Messaggio.SUPPORTO_EMAIL))
                messaggio.terminato = messaggio.ultimo_tentativo
                messaggio.task_id = None
                messaggio.save()

            return risultati

    @staticmethod
    def invia(pk):
        # Non posso lanciare eccezioni dentro transaction.atomic()
        # altrimenti la transazione fa il rollback e il messaggio non viene salvato
        # Quindi per fare raise ritorno l'eccezione come risultato e nel caso la lancio
        with transaction.atomic():
            res = Messaggio.invia_no_lock(pk)
        if isinstance(res, Exception):
            raise res
        return res

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

        messaggi = Messaggio.objects.filter(terminato__isnull=True)
        if dimensione_massima is not None:
            messaggi = messaggi[:dimensione_massima]

        for messaggio in messaggi:
            Messaggio.invia(messaggio.pk)

    @staticmethod
    def costruisci_email(oggetto='Nessun oggetto', modello='email_vuoto.html', corpo=None, mittente=None,
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

        destinatari = destinatari or []
        allegati = allegati or []

        corpo = corpo or {}
        corpo.update({
            'mittente': mittente,
            'allegati': allegati,
        })

        oggetto = Truncator(oggetto).chars(Messaggio.LUNGHEZZA_MASSIMA_OGGETTO)

        with transaction.atomic():
            m = Messaggio(oggetto=oggetto,
                          mittente=mittente,
                          corpo=get_template(modello).render(corpo),
                          **kwargs)
            m.processa_link()
            m.save()

            for d in destinatari:
                m.oggetti_destinatario.create(persona=d)

            for a in allegati:
                a.oggetto = m
                a.save()

            m.save()

            return m

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

        msg = Messaggio.costruisci_email(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente,
                                         destinatari=destinatari, allegati=allegati, **kwargs)
        try:
            Messaggio.invia(msg.pk)
        except ErrorePostaTemporaneo:   # metto in coda celery
            msg.task_id = uuid()
            msg.save()
            invia_mail.apply_async((msg.pk,), task_id=msg.task_id)
        except ErrorePostaFatale:       # pazienza
            pass

        return msg

    @staticmethod
    def costruisci_e_accoda(oggetto=None, modello=None, corpo=None, mittente=None, destinatari=None, allegati=None,
                            **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo alla coda celery.
        :param oggetto: Oggetto deltilizzare per l'invio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio accodato.
        """

        kwargs['task_id'] = uuid()
        msg = Messaggio.costruisci_email(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente,
                                         destinatari=destinatari, allegati=allegati, **kwargs)
        invia_mail.apply_async((msg.pk,), task_id=kwargs['task_id'])
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
    errore = models.CharField(max_length=512, blank=True, null=True, default=None, db_index=True)
