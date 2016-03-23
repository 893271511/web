# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0003_auto_20160315_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='test_env2',
            field=models.ManyToManyField(to='release.Host'),
        ),
    ]
