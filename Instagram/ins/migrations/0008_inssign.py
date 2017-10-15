# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ins', '0007_auto_20171005_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsSign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article', models.ForeignKey(related_name='sign_article', to='ins.InsArticle')),
                ('people', models.ForeignKey(related_name='sign_people', to='ins.InsUser')),
                ('target', models.ForeignKey(related_name='sign_target', to='ins.InsUser')),
            ],
            options={
                'db_table': 'ins_sign',
            },
        ),
    ]
