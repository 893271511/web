# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0013_auto_20160418_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='staging_env',
            field=models.ManyToManyField(related_name='staging_ip', to='release.Host'),
        ),
    ]
