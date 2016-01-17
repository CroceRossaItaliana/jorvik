# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160117_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='conoscenza',
            field=models.CharField(db_index=True, help_text='Come sei venuto/a a conoscenza delle opportunità di volontariato della CRI?', blank=True, choices=[('SI', 'Siti web della Croce Rossa Italiana'), ('FB', 'Facebook'), ('TW', 'Twitter'), ('NW', 'Newsletter'), ('TV', 'TV o Web TV'), ('RA', 'Radio'), ('GI', 'Giornali (online o cartacei)'), ('AM', 'Da un amico, collega o familiare'), ('AF', 'Affissioni (locandine, manifesti, ecc.)'), ('EV', 'Eventi organizzati dalla CRI (es. stand informativi, manifestazioni, open day, ecc.)'), ('SE', 'Partecipazione ad attività e/o fruizione di servizi erogati dalla CRI (es. corsi di formazione, servizi sanitari, servizi sociali, ecc.)'), ('AL', 'Altro')], default=None, null=True, max_length=2),
        ),
    ]
