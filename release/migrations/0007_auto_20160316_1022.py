# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0006_auto_20160316_1012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='test_env2',
            new_name='test_env',
        ),
    ]
