# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    p = apps.get_model("base", "Autorizzazione")
    db_alias = schema_editor.connection.alias

    corrispondenze = {
        "DC":   "CB-PART",
        "PR":   "PRES",
        "RE":   "ATT-PART",
        "US":   "US-GEN"
    }

    #pp = p.objects.using(db_alias).filter(email_contatto__exact='').exclude(utenza__email__isnull=True)
    #tot = pp.count()
    tot = 0
    print(" Ci sono %d autorizzazioni da aggiornare" % (p.objects.using(db_alias).all().count(),))
    for vecchio_ruolo, nuovo_ruolo in corrispondenze.items():
        #print(" => Aggiorno ruolo autorizzazioni: %s => %s..." % (vecchio_ruolo, nuovo_ruolo,))
        auuts = p.objects.using(db_alias).filter(destinatario_ruolo=vecchio_ruolo)
        #print(" ===> %d autorizzazioni da aggiornare " % (auuts.count(),))
        tot += auuts.count()
        #print(" ===> Aggiornamento...")
        auuts.update(destinatario_ruolo=nuovo_ruolo)
        tot += auuts.count()

    print(" Aggiornate %d autorizzazioni." % (tot,))


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    a = 1  # do nothing


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0017_auto_20160120_1524'),
        ('base', '0004_auto_20160120_1524')

    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
