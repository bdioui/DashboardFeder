# Generated by Django 3.1.7 on 2021-04-13 14:06

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dash', '0016_auto_20210413_1401'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='indicateurs',
            new_name='Indicateur',
        ),
    ]
