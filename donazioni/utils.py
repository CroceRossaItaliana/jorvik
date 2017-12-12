from collections import OrderedDict
from datetime import timedelta
from itertools import groupby

from django.conf import settings
from django.template.loader import get_template

from base.utils import poco_fa
from donazioni.models import TokenRegistrazioneDonatore, AssociazioneDonatorePersona
from posta.models import Messaggio


def invia_mail_ringraziamento(donatore, campagna, gia_registrato=None):
    """
    Invia email di ringraziamento con il testo specifico della campagna
    :param donatore: oggetto Donatore
    :param campagna: oggetto Campagna
    :param gia_registrato: oggetto AssociazioneDonatorePersona
    se il donatore si è già registrato a seguito di una donazione precedente, altrimenti None
    :return: link di registrazione a scopo di DEBUG
    """
    testo_email = campagna.testo_email_ringraziamento
    host_registrazione = 'https://gaia.cri.it/' if not settings.DEBUG else 'http://127.0.0.1:8000/'

    if not gia_registrato:
        destinatario = donatore.email
        oggetto = 'Ciao {}'.format(donatore.nome_completo)
        token = TokenRegistrazioneDonatore.genera(donatore, campagna.organizzatore)
        vista_registrazione = 'registrati/soggetto_donatore/credenziali/' if donatore.codice_fiscale else 'registrati/soggetto_donatore/codice_fiscale/'
        link = '{}{}?t={}'.format(host_registrazione, vista_registrazione, token)
        testo_link = 'Registrati'
    else:
        persona = gia_registrato.persona
        oggetto = 'Ciao {}'.format(persona.nome_completo)
        link = '{}login/'.format(host_registrazione)
        destinatario = persona.email_contatto
        testo_link = 'Accedi'

    corpo = {'testo': testo_email,
             'testo_link': testo_link,
             'donatore': donatore,
             'link_registrazione': link,
             'campagna': campagna}
    if campagna.id_lista_mailup:
        corpo.update({'url_registrazione_mailup': campagna.url_modulo_mailup,
                      'testo_link_mailup': 'Iscriviti alla newsletter della campagna!'})

    Messaggio.invia_raw(
        oggetto=oggetto,
        corpo_html=get_template('email_ringraziamento_donazione_economica.html').render(corpo),
        email_mittente=None,
        lista_email_destinatari=[destinatario]
    )
    return link


def invia_notifica_donatore(donazione):
    donatore = donazione.donatore
    if not donatore.email:
        return 'Il Donatore non ha lasciato una mail in fase di registrazione della donazione', False
    campagna = donazione.campagna
    registrazione_donatore_persona = AssociazioneDonatorePersona.objects.filter(donatore=donatore).first() or None
    invia_mail_ringraziamento(donatore, campagna, registrazione_donatore_persona)
    return 'Notifica inviata!', True


def crea_lista_mailup(campagna):
    sede = campagna.organizzatore
    responsabile = campagna.responsabili_attuali.first()
    body = {
        'Name': campagna.nome,
        'Business': True,
        'Customer': True,

        'OwnerEmail': sede.presidente().email,
        'Description': "Mailing list per la campagna donazioni economiche {}".format(campagna.nome),
        'ReplyTo': responsabile.email,

        'Format': 'html',
        'NLSenderName': responsabile.nome_completo,
        'CompanyName': 'CRI: {}'.format(sede.nome_completo),
        'ContactName': responsabile.nome_completo,
        'Address': sede.locazione.indirizzo,
        'City': sede.locazione.comune,
        'CountryCode': sede.locazione.stato.code,
        'PermissionReminder': "Ricevi questa email perch\\u00e9 sei registrato "
                              "alla newsletter della campagna donazioni economiche {}".format(campagna.nome),
        'WebSiteUrl': sede.sito_web or 'https://gaia.cri.it/',
        "UseDefaultSettings": True,
        'Phone': sede.telefono or '3341954461',
        'PostalCode': sede.locazione.cap,
        'StateOrProvince': sede.locazione.provincia_breve,
        'TimeZoneCode': "UTC+01:00.0",
        'Charset': "UTF-8",
        'SubscribedEmail': False,
        'BouncedEmail': responsabile.email,
        'FrontendForm': True,
        'Public': True,
        'ScopeCode': 0,
        'TrackOnOpened': True,
        'OptoutType': 3,
        'SendEmailOptout': False,
        'Disclaimer': "Per l'informativa sulla privacy D.Lgs 196/2003 visitare "
                      "l'home page del sito. <br/> Policy AntiSPAM garantita da "
                      "<a href=\"http://www.mailup.it/email-marketing/policy-antispam.asp\" target=_blank>"
                      "<img src=\"http://doc.mailupnet.it/logo_small_R.gif\" border=\"0\" align=\"middle\" /></a>",
        'HeaderListUnsubscriber': "<[listunsubscribe]>,<[mailto_uns]>",
        'HeaderXAbuse': "Please report abuse here:  http://www.mailup.it/email-marketing/Policy-antispam_ENG.asp",

        'SmsSenderName': responsabile.nome_completo,
        'DefaultPrefix': "0039",
        'SendConfirmSms': False,
        'MultipartText': True,
        'KBMax': 300,
        'NotifyEmail': responsabile.email,
        'idSettings': 1,
        'ConversionlabTrackCode': '',
        'LinkTrackingParameters': '',

    }

    client_mailup = sede.account_mailup

    res = client_mailup.crea_lista(body)
    return res


def iscrivi_email(campagna, id_lista, nome, email, telefono):
    body = {
        "Name": nome or '',
        "Email": email,
        "MobileNumber": telefono or '',
        "MobilePrefix": "0039"
    }
    sede = campagna.organizzatore
    client_mailup = sede.account_mailup
    res = client_mailup.iscrivi_email(id_lista, body)
    return res


def donazioni_per_mese_anno(donazioni):
    donazioni_mese_anno = groupby(donazioni, key=lambda i: (i.data.month, i.data.year))
    totali = OrderedDict()
    for k, grp in donazioni_mese_anno:
        grp = list(grp)
        totali[k] = {'totale': sum(d.importo for d in grp), 'count': len(grp)}
    return totali


def donazioni_chart_52_settimane(donazioni):
    data_52_settimane_fa = poco_fa() - timedelta(weeks=52)
    donazioni = donazioni.filter(data__gte=data_52_settimane_fa)
    donazioni_settimana = groupby(donazioni, key=lambda i: (int(i.data.date().isocalendar()[1])))
    labels = []
    importi = []
    num_donazioni = []
    export = OrderedDict()
    range_52 = iter(range(1, 53))
    for k, grp in donazioni_settimana:
        i = next(range_52)
        grp = list(grp)
        if k > i:
            # riempi settimane mancanti con valori nulli
            for riempitivo in range(i, k):
                export['W%s' % riempitivo] = {'count': 0, 'totale': 0.0}
                labels.append('W%s' % riempitivo)
                num_donazioni.append(0)
                importi.append(0.0)
                next(range_52)
        export['W%s' % k] = {'count': len(grp), 'totale': sum(d.importo for d in grp)}
        labels.append('W%s' % k)
        num_donazioni.append({'meta': '# donazioni', 'value': len(grp)})
        importi.append({'meta': 'importo', 'value': sum(d.importo for d in grp)})
    statistiche = {'labels': labels,
                   'num_donazioni': num_donazioni,
                   'importi': importi}
    return statistiche, export
