from anagrafica.models import Sede, Appartenenza
from anagrafica.permessi.applicazioni import PERMESSI_NOMI_DICT
from jorvik import settings
import requests


PRESIDENTE = '211091'
COMMISSARIO = '211092'

CONSIGLIERE = '213305'


def trippus_oauth():
    payload = 'grant_type=password&username={}&password={}'.format(
        settings.TRIPPUS_USERNAME,
        settings.TRIPPUS_PASSWORD
    )
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    res = requests.post(
        "{}/oauth/token".format(settings.TRIPPUS_DOMAIN),
        headers=headers,
        data=payload
    )

    return res.json()


def trippus_booking(persona=None, access_token=''):
    if persona.is_presidente:
        delega = persona.delega_presidente
        sede = delega.oggetto
        codice = PRESIDENTE
    elif persona.is_delegato_assemblea_nazionale:
        delega = persona.delega_delegato_assemblea_nazionale
        sede = delega.oggetto
        codice = PRESIDENTE
    elif persona.is_responsabile_area_delegato_assemblea_nazionale:
        delega = None
        sede = Sede.objects.get(pk=1)
        codice = PRESIDENTE
    elif persona.is_comissario:
        delega = persona.delega_commissario
        sede = delega.oggetto
        codice = COMMISSARIO
    else:
        delega = None
        sede = None
        codice = None

    payload = {
      "participants": [
        {
          "properties": [
                {
                  "key": "Firstname",
                  "value": persona.nome,
                  "type": "Standard"
                } if persona.nome else None,
                {
                  "key": "Lastname",
                  "value": persona.cognome,
                  "type": "Standard"
                } if persona.cognome else None,
                {
                  "key": "Email",
                  "value": persona.email if persona.email else persona.utenza.email,
                  "type": "Standard"
                },
                {
                  "key": "Comitato",
                  "value": sede.nome,
                  "type": "Web"
                },
                {
                  "key": "Ruolo",
                  "value": PERMESSI_NOMI_DICT[delega.tipo] if delega else 'Consigliere',
                  "type": "Web"
                },
                {
                  "key": "CountryCode",
                  "value": "+39",
                  "type": "Standard"
                }
            ]
        }
      ]
    }

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }

    res = requests.post(
        "{}/v1/categories/{}/booking-sources".format(
            settings.TRIPPUS_DOMAIN,
            codice
        ),
        headers=headers,
        json=payload
    )

    return res.json()


def trippus_booking_consiglieri(persona=None, access_token=''):
    if persona.is_consigliere_giovane:
        delega = persona.delega_consigliere_giovane
        sede = delega.oggetto
        codice = CONSIGLIERE
    elif persona.is_responsabile_area_delegato_assemblea_nazionale_giovani:
        delega = persona.delega_responsabile_area_delegato_assemblea_nazionale_giovani
        sede = delega.oggetto.sede
        codice = CONSIGLIERE
    elif persona.volontario:
        appartenenza = Appartenenza.objects.filter(
            persona=persona, fine=None, membro=Appartenenza.VOLONTARIO, terminazione=None
        ).first()
        sede = appartenenza.sede
        codice = CONSIGLIERE
    else:
        sede = None
        codice = None

    payload = {
      "participants": [
        {
          "properties": [
                {
                  "key": "Firstname",
                  "value": persona.nome,
                  "type": "Standard"
                } if persona.nome else None,
                {
                  "key": "Lastname",
                  "value": persona.cognome,
                  "type": "Standard"
                } if persona.cognome else None,
                {
                  "key": "Email",
                  "value": persona.email if persona.email else persona.utenza.email,
                  "type": "Standard"
                },
                {
                  "key": "Comitato",
                  "value": sede.nome ,
                  "type": "Web"
                },
                {
                  "key": "Ruolo",
                  "value": "Consigliere Giovane",
                  "type": "Web"
                },
                {
                  "key": "CountryCode",
                  "value": "+39",
                  "type": "Standard"
                }
            ]
        }
      ]
    }

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }

    res = requests.post(
        "{}/v1/categories/{}/booking-sources".format(
            settings.TRIPPUS_DOMAIN,
            codice
        ),
        headers=headers,
        json=payload
    )

    return res.json()
