# Generated by Django 5.2.4 on 2025-07-20 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_manager',
            field=models.BooleanField(default=False, verbose_name='Est Responsable'),
        ),
    ]
