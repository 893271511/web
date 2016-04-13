# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0010_auto_20160413_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='port',
            field=models.PositiveIntegerField(),
            preserve_default=False,
        ),
    ]
