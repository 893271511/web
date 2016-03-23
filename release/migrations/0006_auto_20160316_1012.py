# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0005_remove_project_test_env'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='test_env2',
            field=models.ManyToManyField(to='release.Host', related_name='Host_ip'),
        ),
    ]
