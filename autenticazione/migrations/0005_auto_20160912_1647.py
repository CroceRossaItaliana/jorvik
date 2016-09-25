# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import Permission, Group
from django.db import migrations
# auth.view_group 


def forwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.using(db_alias).get(
        app_label="auth",
        model="group"
    )
    Permission = apps.get_model("auth","Permission") 
    Permission(
        name='Can view group',
        content_type=content_type,
        codename='view_group',
    ).save()
    

def backwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.using(db_alias).get(
        app_label="auth",
        model="group"
    )
    Permission = apps.get_model("auth","Permission") 
    Permission.objects.get(
        name='Can view group',
        content_type=content_type,
        codename='view_group',
    ).delete()   

class Migration(migrations.Migration):

    dependencies = [
        ('autenticazione', '0004_auto_20160906_1702'),
    ]

    operations = [
        migrations.RunPython(
            forwards,
            backwards,
        ),    
    ]
