# Generated by Django 4.2.6 on 2023-10-15 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0003_event_hour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='group',
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gym_manager_api.group'),
        ),
    ]
