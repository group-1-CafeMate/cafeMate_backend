# Generated by Django 5.0.4 on 2024-12-30 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cafeInfo", "0003_remove_cafe_open_hour_alter_cafe_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="metrostation",
            name="metro_station_id",
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
