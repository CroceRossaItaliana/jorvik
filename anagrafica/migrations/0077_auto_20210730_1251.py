# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-07-30 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0076_auto_20210617_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='conoscenza',
            field=models.CharField(choices=[('SI', 'Siti web della Croce Rossa Italiana'), ('FB', 'Facebook'), ('TW', 'Twitter'), ('NW', 'Newsletter'), ('TV', 'TV o Web TV'), ('RA', 'Radio'), ('GI', 'Giornali (online o cartacei)'), ('AM', 'Da un amico, collega o familiare'), ('AF', 'Affissioni (locandine, manifesti, ecc.)'), ('EV', 'Eventi organizzati dalla CRI (es. stand informativi, manifestazioni, open day, ecc.)'), ('SE', 'Partecipazione ad attività e/o fruizione di servizi erogati dalla CRI (es. corsi di formazione, servizi sanitari, servizi sociali, ecc.)'), ('MF', 'Pubblicità MEDIAFRIENDS'), ('AL', 'Altro')], db_index=True, default=None, help_text='Come sei venuto/a a conoscenza delle opportunità di volontariato della CRI?', max_length=2, null=True),
        ),
    ]