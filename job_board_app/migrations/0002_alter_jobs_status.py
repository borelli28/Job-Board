# Generated by Django 3.2.5 on 2021-07-15 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='status',
            field=models.CharField(default='viewed', max_length=20),
        ),
    ]
