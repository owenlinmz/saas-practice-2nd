# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='bk_cloud_id',
            field=models.IntegerField(default=0, verbose_name='\u4e91\u533a\u57dfID'),
            preserve_default=False,
        ),
    ]
