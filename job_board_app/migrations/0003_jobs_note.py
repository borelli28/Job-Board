# Generated by Django 3.2.5 on 2021-07-16 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board_app', '0002_alter_jobs_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='note',
            field=models.TextField(default='Enter text here'),
        ),
    ]
