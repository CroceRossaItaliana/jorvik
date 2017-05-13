from django.db import migrations, models
from datetime import datetime, timedelta


def forwards_func(apps, schema_editor):
    Messaggio = apps.get_model("posta", "Messaggio")

    MANTIENI_MESI = 6
    mesi_fa = datetime.now() - timedelta(days=30 * MANTIENI_MESI)
    posta_obsoleta = Messaggio.objects.filter(creazione__lte=mesi_fa)
    posta_obsoleta_count = posta_obsoleta.count()

    print("  => 0010 ci sono %d messaggi obsoleti (oltre %d mesi) da cancellare" % (posta_obsoleta_count, MANTIENI_MESI))

    posta_obsoleta.update(eliminato=True, corpo="")


class Migration(migrations.Migration):
    dependencies = [
        ('posta', '0009_messaggio_eliminato'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
