# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-15 05:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feasta', '0004_auto_20160416_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='year',
            field=models.CharField(choices=[(b'2016', b'2016'), (b'2017', b'2017'), (b'2018', b'2018'), (b'2019', b'2019'), (b'2020', b'2020'), (b'2021', b'2021'), (b'2022', b'2022'), (b'2023', b'2023'), (b'2024', b'2024'), (b'2025', b'2025')], default=2017, max_length=4),
        ),
    ]
