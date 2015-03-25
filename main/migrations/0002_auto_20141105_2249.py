# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodeposition',
            name='describes_by_label',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='nodeposition',
            name='describes_by_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
