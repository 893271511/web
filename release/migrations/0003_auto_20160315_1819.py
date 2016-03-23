# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0002_project_test_env4'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='test_env2',
        ),
        migrations.RemoveField(
            model_name='project',
            name='test_env3',
        ),
        migrations.RemoveField(
            model_name='project',
            name='test_env4',
        ),
        migrations.AlterField(
            model_name='project',
            name='test_env',
            field=models.ForeignKey(related_name='Host_ip', to='release.Host'),
        ),
    ]
