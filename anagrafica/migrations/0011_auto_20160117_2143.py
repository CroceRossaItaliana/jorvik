# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0010_auto_20160117_2142'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='riserva',
            options={'verbose_name': 'Richiesta di trasferimento', 'verbose_name_plural': 'Richieste di trasferimento'},
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='info',
            field=models.CharField(max_length=512, help_text='Maggiori informazioni sulla causa della dimissione'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='conoscenza',
            field=models.CharField(default=None, null=True, max_length=2, db_index=True, choices=[('SI', 'Siti web della Croce Rossa Italiana'), ('FB', 'Facebook'), ('TW', 'Twitter'), ('NW', 'Newsletter'), ('TV', 'TV o Web TV'), ('RA', 'Radio'), ('GI', 'Giornali (online o cartacei)'), ('AM', 'Da un amico, collega o familiare'), ('AF', 'Affissioni (locandine, manifesti, ecc.)'), ('EV', 'Eventi organizzati dalla CRI (es. stand informativi, manifestazioni, open day, ecc.)'), ('SE', 'Partecipazione ad attività e/o fruizione di servizi erogati dalla CRI (es. corsi di formazione, servizi sanitari, servizi sociali, ecc.)'), ('AL', 'Altro')], help_text='Come sei venuto/a a conoscenza delle opportunità di volontariato della CRI?'),
        ),
    ]
