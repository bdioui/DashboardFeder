# Generated by Django 3.1.7 on 2021-04-13 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0017_auto_20210413_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicateur',
            name='numero_op',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
