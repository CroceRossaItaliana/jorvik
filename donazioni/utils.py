from django.conf import settings
from django.template.loader import get_template

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
