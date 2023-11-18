# Generated by Django 4.2.6 on 2023-10-21 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0006_alter_scheduler_first_alter_scheduler_last'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='event',
            name='unique_event',
        ),
        migrations.RemoveField(
            model_name='event',
            name='hour',
        ),
        migrations.RemoveField(
            model_name='scheduler',
            name='hour',
        ),
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(fields=('date', 'group'), name='unique_event'),
        ),
    ]