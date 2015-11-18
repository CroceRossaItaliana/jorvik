"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
from smtplib import SMTPException
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags
from base.models import *
from base.tratti import *
from social.models import ConGiudizio
from lxml import html

class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConAllegati):

    SUPPORTO_EMAIL = 'supporto@gaia.cri.it'
    SUPPORTO_NOME = 'Supporto Gaia'

    class Meta:
        verbose_name = "Messaggio di posta"
        verbose_name_plural = "Messaggi di posta"

    oggetto = models.CharField(max_length=128, db_index=True, blank=False, default="(Nessun oggetto)")
    corpo = models.TextField(blank=True, null=False, default="(Nessun corpo)")

    ultimo_tentativo = models.DateTimeField(blank=True, null=True, default=None)
    terminato = models.DateTimeField(blank=True, null=True, default=None)

    # Il mittente e' una persona o None (il sistema di Gaia)
    mittente = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True)

    @property
    def destinatari(self):
        """
        Ritorna la lista di tutti gli oggetti Persona destinatari di questo messaggio.
        :return:
        """
        return [x.persona for x in self.oggetti_destinatario.all()]

    @property
    def corpo_body(self):
        """
        Prova ad estrarre il corpo della pagina (body).
        :return:
        """
        doc = html.document_fromstring(self.corpo)
        body = doc.xpath('//body')[0]
        body.tag = 'div'
        #try:
        return html.tostring(body)
        #except:
        #    return self.corpo
        #print html.parse('http://someurl.at.domain').xpath('//body')[0].text_content()


    def accoda(self):
        """
        Salva e accoda il messaggio per l'invio asincrono.
        :return:
        """
        pass

    def allegati_pronti(self):
        return ()

    def invia(self):
        """
        Salva e invia immediatamente il messaggio.
        :return:
        """
        self.save()  # Assicurati che sia salvato

        if self.mittente is None:
            mittente_nome = self.SUPPORTO_NOME
            mittente_email = self.SUPPORTO_EMAIL
        else:
            mittente_nome = self.mittente.nome_completo
            mittente_email = self.mittente.email

        mittente = mittente_nome + " <" + mittente_email + ">"

        plain_text = strip_tags(self.corpo)
        successo = True

        if not self.oggetti_destinatario:
            try:
                msg = EmailMultiAlternatives(
                    subject=self.oggetto,
                    body=plain_text,
                    from_email=mittente,
                    to=[self.SUPPORTO_EMAIL],
                    attachments=self.allegati_pronti(),
                )
                msg.attach_alternative(self.corpo, "text/html")
                msg.send()
            except SMTPException:
                successo = False

        for d in self.oggetti_destinatario.all():

            try:
                msg = EmailMultiAlternatives(
                    subject=self.oggetto,
                    body=plain_text,
                    from_email=mittente,
                    to=[d.persona.email],
                    attachments=self.allegati_pronti(),
                )
                msg.attach_alternative(self.corpo, "text/html")
                msg.send()
                d.inviato = True

            except SMTPException as e:
                successo = False
                d.errore = str(e)

            d.tentativo = datetime.now()
            d.save()

        if successo:
            self.terminato = datetime.now()

        self.ultimo_tentativo = datetime.now()
        self.save()

    def aggiungi_destinatario(self, persona):
        """
        Aggiunge un destinatario al messaggio di posta.
        Il messaggio DEVE essere salvato.
        :param persona: La Persona da aggiungere.
        :return:
        """
        d = Destinatario(messaggio=self, persona=persona)
        return d.save()

    @classmethod
    def costruisci(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], **kwargs):
        m = cls(
            oggetto=oggetto,
            mittente=mittente,
            corpo=get_template(modello).render(Context(corpo))
        )
        m.save()
        for d in destinatari:
            m.aggiungi_destinatario(d)
        return m

    @classmethod
    def costruisci_e_invia(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo immediatamente.
         IMPORTANTE. Non adatto per messaggi con molti destinatari. In caso di fallimento immediato, il messaggio
                     viene accodato per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :return: Un oggetto Messaggio inviato.
        """
        m = cls.costruisci(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente, destinatari=destinatari, **kwargs)
        m.invia()
        return m

    @classmethod
    def costruisci_e_accoda(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e accodarlo per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :return: Un oggetto Messaggio accodato.
        """
        m = cls.costruisci(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente, destinatari=destinatari, **kwargs)
        m.accoda()
        return m

    def __str__(self):
        return self.oggetto


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"

    messaggio = models.ForeignKey(Messaggio, null=False, blank=True, related_name='oggetti_destinatario')
    persona = models.ForeignKey("anagrafica.Persona", null=True, blank=True, default=None)

    inviato = models.BooleanField(default=False)
    tentativo = models.DateTimeField(default=None, blank=True, null=True)
    errore = models.CharField(max_length=256, blank=True, null=True, default=None)
