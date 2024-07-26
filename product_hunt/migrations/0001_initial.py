# Generated by Django 4.2.11 on 2024-07-26 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Website",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("price", models.CharField(default="$ 0.0", max_length=255)),
                ("reviews", models.TextField()),
                ("product_url", models.URLField()),
                ("image_url", models.URLField()),
                ("sentiment_score", models.FloatField(default=0.5)),
                (
                    "sentiment_label",
                    models.CharField(default="Neutral", max_length=255),
                ),
                ("keyword", models.CharField(max_length=255)),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="product_hunt.website",
                    ),
                ),
            ],
        ),
    ]
