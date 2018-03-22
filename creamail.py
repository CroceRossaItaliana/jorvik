#!/usr/bin/env python
import sys
import os
import django
from random import randint

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Utilizzo: {} numero_email'.format(sys.argv[0]))
        raise SystemExit

    try:
        count = int(sys.argv[1])
    except ValueError:
        print('Numero di email non valido')
        raise SystemExit

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jorvik.settings')
    django.setup()

    from posta.models import Messaggio
    from posta.tasks import crea_email
    from anagrafica.models import Persona

    Messaggio.objects.all().delete()

    persone = iter(Persona.objects.all().order_by('?'))
    for n in range(count):
        try:
            mittente = next(persone).pk
            destinatari = [next(persone).pk for _ in range(randint(0, 5))]
            job = crea_email.delay(oggetto='Prova email numero {}'.format(n + 1),
                                   modello='test_email.html',
                                   mittente=mittente,
                                   destinatari=destinatari)
        except StopIteration:
            persone = iter(Persona.objects.all().order_by('?')) # rewind
