# Generated by Django 5.2.1 on 2025-05-16 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onts', '0005_rename_path_onts_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='onts',
            name='lastconupd',
            field=models.DateTimeField(null=True),
        ),
    ]
