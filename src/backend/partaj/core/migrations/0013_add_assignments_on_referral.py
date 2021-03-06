# Generated by Django 2.2.7 on 2020-04-22 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0012_remove_subject_field_from_referral"),
    ]

    operations = [
        migrations.AlterField(
            model_name="referral",
            name="user",
            field=models.ForeignKey(
                blank=True,
                help_text="User who created the referral",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="referrals_created",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.CreateModel(
            name="ReferralAssignment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        editable=False,
                        help_text="Primary key for the assignment",
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
                    "assignee",
                    models.ForeignKey(
                        help_text="User is assigned to work on the referral",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="assignee",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who created the assignment",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="created_by",
                    ),
                ),
                (
                    "referral",
                    models.ForeignKey(
                        help_text="Referral the assignee is linked with",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.Referral",
                        verbose_name="referral",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        blank=True,
                        help_text="Unit under which the assignment was created",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.Unit",
                        verbose_name="unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "referral assignment",
                "db_table": "partaj_referralassignment",
                "unique_together": {("assignee", "referral")},
            },
        ),
        migrations.AddField(
            model_name="referral",
            name="assignees",
            field=models.ManyToManyField(
                help_text="Partaj users that have been assigned to work on this referral",
                related_name="referrals_assigned",
                through="core.ReferralAssignment",
                to=settings.AUTH_USER_MODEL,
                verbose_name="assignees",
            ),
        ),
    ]
