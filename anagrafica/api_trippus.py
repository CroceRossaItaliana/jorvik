from jorvik import settings
import requests


PRESIDENTE = '210905'
COMMISSARIO = '210915'


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
                  "value": persona.email,
                  "type": "Standard"
                } if persona.email else None,
                # {
                #   "key": "Username",
                #   "value": persona.utenza.email,
                #   "type": "Standard"
                # }
            ]
        }
      ]
    }
    print(payload)
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }

    res = requests.post(
        "{}/v1/categories/{}/booking-sources".format(
            settings.TRIPPUS_DOMAIN,
            PRESIDENTE if persona.is_presidente else COMMISSARIO
        ),
        headers=headers,
        json=payload
    )

    return res.json()

