# Generated by Django 3.1.7 on 2021-03-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0004_auto_20210325_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dossier',
            name='DP_CT_depot',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='DP_certif',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='montant_CT',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='montant_UE',
            field=models.FloatField(blank=True, null=True),
        ),
    ]