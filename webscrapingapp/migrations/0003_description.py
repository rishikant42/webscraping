# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webscrapingapp', '0002_query_weburl'),
    ]

    operations = [
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1000)),
                ('description', models.CharField(max_length=10000)),
            ],
        ),
    ]