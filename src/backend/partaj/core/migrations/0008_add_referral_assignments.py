# Generated by Django 2.2.7 on 2020-04-08 14:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0007_make_unitmemberships_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReferralAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Primary key for the topic as UUID",
                        primary_key=True,
                        serialize=False,
                        verbose_name="id",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "assigned_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="Unit organizer who created the assignment",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="assigned by",
                    ),
                ),
                (
                    "assignee",
                    models.ForeignKey(
                        help_text="Unit member tasked with handling the linked referral",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="assignee",
                    ),
                ),
                (
                    "referral",
                    models.ForeignKey(
                        help_text="Referral the linked unit member is talked with handling",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.Referral",
                        verbose_name="referral",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        help_text="Unit under which this assignment is created",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.Unit",
                        verbose_name="unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "referral assignment",
                "db_table": "partaj_referral_assignment",
                "unique_together": {("assignee", "referral")},
            },
        ),
    ]
