# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0006_auto_20160117_1525'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='privacy',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='privacy',
            name='persona',
        ),
        migrations.AddField(
            model_name='persona',
            name='privacy_contatti',
            field=models.SmallIntegerField(choices=[(9, 'Pubblico, inclusi utenti non registrati'), (7, 'Solo utenti registrati di Gaia'), (5, 'A tutti i membri della mia Sede CRI'), (3, 'Ai Responsabili della mia Sede CRI')], help_text='A chi mostrare il mio indirizzo e-mail e i miei numeri di telefono.', default=5, db_index=True),
        ),
        migrations.AddField(
            model_name='persona',
            name='privacy_curriculum',
            field=models.SmallIntegerField(choices=[(9, 'Pubblico, inclusi utenti non registrati'), (7, 'Solo utenti registrati di Gaia'), (5, 'A tutti i membri della mia Sede CRI'), (3, 'Ai Responsabili della mia Sede CRI')], help_text='A chi mostrare il mio curriculum (competenze pers., patenti, titoli di studio e CRI)', default=3, db_index=True),
        ),
        migrations.AddField(
            model_name='persona',
            name='privacy_deleghe',
            field=models.SmallIntegerField(choices=[(9, 'Pubblico, inclusi utenti non registrati'), (7, 'Solo utenti registrati di Gaia'), (5, 'A tutti i membri della mia Sede CRI'), (3, 'Ai Responsabili della mia Sede CRI')], help_text='A chi mostrare i miei incarichi, come presidenze, referenze attività, deleghe, ecc.', default=3, db_index=True),
        ),
        migrations.DeleteModel(
            name='Privacy',
        ),
    ]
