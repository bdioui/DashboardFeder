# Generated by Django 3.1.7 on 2021-04-13 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0012_auto_20210406_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='indicateurs_data',
            field=models.FileField(null=True, upload_to='indicateurs_data'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_data',
            field=models.FileField(null=True, upload_to='user_data'),
        ),
    ]
