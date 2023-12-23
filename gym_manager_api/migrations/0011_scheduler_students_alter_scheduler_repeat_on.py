# Generated by Django 4.2.6 on 2023-12-08 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0010_remove_scheduler_classroom_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduler',
            name='students',
            field=models.ManyToManyField(to='gym_manager_api.student'),
        ),
        migrations.AlterField(
            model_name='scheduler',
            name='repeat_on',
            field=models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=3, null=True),
        ),
    ]
