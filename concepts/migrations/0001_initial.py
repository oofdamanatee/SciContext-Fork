# Generated by Django 5.2.1 on 2025-05-16 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('onts', '0005_rename_path_onts_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concepts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('updated', models.DateTimeField()),
                ('ont_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='onts.onts')),
            ],
            options={
                'db_table': 'concepts',
                'managed': True,
            },
        ),
    ]
