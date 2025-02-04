# Generated by Django 5.0.4 on 2024-12-28 10:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_remove_profile_date_profile_date_joined_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="date_joined",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="is_admin",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="last_login",
        ),
        migrations.AddField(
            model_name="profile",
            name="date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="profile",
            name="email",
            field=models.EmailField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="profile",
            name="password",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name="profile",
            name="username",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
