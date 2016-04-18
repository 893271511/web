# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0012_auto_20160413_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='port',
            field=models.PositiveIntegerField(),
        ),
    ]
