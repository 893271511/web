# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='test_env4',
            field=models.GenericIPAddressField(),
            preserve_default=False,
        ),
    ]
