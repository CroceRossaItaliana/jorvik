from anagrafica.models import Sede, Appartenenza
from anagrafica.permessi.applicazioni import PERMESSI_NOMI_DICT
from jorvik import settings
import requests


PRESIDENTE = '235790'
COMMISSARIO = '235793'
DELEGATI_TECNICI_NAZIONALI = '225211'
RESPONSABILI_UO = '225212'
DIRETTORICRI = '225213'

CONSIGLIERE = '213305'

VOLONTARE = "220735"


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
        _delega = persona.delega_presidente
        sede = _delega.oggetto
        if _delega:
          delega = PERMESSI_NOMI_DICT[_delega.tipo]
        else:
          delega = None
        codice = PRESIDENTE
    elif persona.is_comissario:
        _delega = persona.delega_commissario
        sede = _delega.oggetto
        if _delega:
          delega = PERMESSI_NOMI_DICT[_delega.tipo]
        else:
          delega = None
        codice = COMMISSARIO
    elif persona.is_delegato_assemblea_nazionale:
        _delega = persona.delega_delegato_assemblea_nazionale
        sede = _delega.oggetto
        if _delega:
          delega = PERMESSI_NOMI_DICT[_delega.tipo]
        else:
          delega = None
        codice = PRESIDENTE
    elif persona.is_responsabile_area_delegato_assemblea_nazionale:
        delega = None
        sede = Sede.objects.get(pk=1)
        codice = PRESIDENTE
    elif persona.is_responsabile_uo_assemblea_nazionale:
        delega = "Responsabile U.O."
        sede = Sede.objects.get(pk=1)
        codice = RESPONSABILI_UO
    elif persona.is_delegato_tecnico_assemblea_nazionale:
        delega = "Delegato Tecnico Nazionale"
        sede = Sede.objects.get(pk=1)
        codice = DELEGATI_TECNICI_NAZIONALI
    elif persona.is_direttorecri_assemblea_nazionale:
        delega = "Direttore CRI"
        sede = Sede.objects.get(pk=1)
        codice = DIRETTORICRI
        
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
                  "key": "Codice Fiscale",
                  "value": persona.codice_fiscale,
                  "type": "Web"
                } if persona.codice_fiscale else None,
                {
                  "key": "Comitato",
                  "value": sede.nome,
                  "type": "Web"
                },
                {
                  "key": "Ruolo",
                  "value": delega if delega else 'Ispettori',
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


def trippus_booking_volontari(persona=None, access_token=''):
    if persona.volontario:
        appartenenza = Appartenenza.objects.filter(
            persona=persona, fine=None, membro=Appartenenza.VOLONTARIO, terminazione=None
        ).first()
        # Questa puo essere piu di un sede
        sede = appartenenza.sede
        codice = VOLONTARE
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
                  "value": sede.nome,
                  "type": "Web"
                },
                {
                  "key": "Ruolo",
                  "value": 'Volontari',
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
