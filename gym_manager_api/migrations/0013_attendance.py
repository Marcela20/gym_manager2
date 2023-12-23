# Generated by Django 4.2.6 on 2023-12-09 19:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0012_remove_group_students_scheduler_start_hour'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('PAI', 'paid'), ('UNP', 'unpaid'), ('PPR', 'paid present'), ('UPR', 'unpaid present'), ('UNP', 'unpaid not present'), ('PNP', 'paid not present')], default='UNP', max_length=3)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gym_manager_api.group')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gym_manager_api.student')),
            ],
        ),
    ]