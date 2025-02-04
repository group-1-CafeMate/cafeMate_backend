# Generated by Django 5.0.4 on 2024-12-25 17:20

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=50)),
                ("username", models.CharField(blank=True, max_length=20)),
                ("password", models.CharField(blank=True, max_length=150)),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
