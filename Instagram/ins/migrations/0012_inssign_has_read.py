# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-10 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ins', '0011_remove_inssign_has_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='inssign',
            name='has_read',
            field=models.BooleanField(default=False),
        ),
    ]
