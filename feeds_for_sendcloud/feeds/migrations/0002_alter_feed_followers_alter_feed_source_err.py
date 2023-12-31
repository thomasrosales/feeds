# Generated by Django 4.0.8 on 2023-11-17 20:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("feeds", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feed",
            name="followers",
            field=models.ManyToManyField(blank=True, related_name="feeds", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="feed",
            name="source_err",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
