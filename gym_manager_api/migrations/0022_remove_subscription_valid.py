# Generated by Django 4.2.6 on 2023-12-25 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0021_alter_subscription_valid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='valid',
        ),
    ]