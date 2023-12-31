# Generated by Django 4.2.6 on 2023-12-22 12:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0015_alter_attendance_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entrances', models.IntegerField()),
                ('valid_until', models.DateField(default=django.utils.timezone.now)),
                ('valid_since', models.DateField(default=django.utils.timezone.now)),
                ('entrances_left', models.IntegerField()),
                ('schedulers', models.ManyToManyField(to='gym_manager_api.scheduler')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscription', to='gym_manager_api.student')),
            ],
        ),
    ]
