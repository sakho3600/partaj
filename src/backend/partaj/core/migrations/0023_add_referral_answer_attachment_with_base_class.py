# Generated by Django 3.0.5 on 2020-06-16 09:37

from django.db import migrations, models
import django.db.models.deletion
import partaj.core.models.attachment
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_update_table_names_for_activity_and_answer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="referralattachment",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Primary key for the attachment as UUID",
                primary_key=True,
                serialize=False,
                verbose_name="id",
            ),
        ),
        migrations.AlterField(
            model_name="referralattachment",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="Name for the attachment, defaults to file name",
                max_length=200,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="referralattachment",
            name="referral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attachments",
                related_query_name="attachment",
                to="core.Referral",
                verbose_name="referral",
            ),
        ),
        migrations.CreateModel(
            name="ReferralAnswerAttachment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Primary key for the attachment as UUID",
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
                    "file",
                    models.FileField(
                        upload_to=partaj.core.models.attachment.attachment_upload_to,
                        verbose_name="file",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Name for the attachment, defaults to file name",
                        max_length=200,
                        verbose_name="name",
                    ),
                ),
                (
                    "size",
                    models.IntegerField(
                        blank=True,
                        help_text="Attachment file size in bytes",
                        null=True,
                        verbose_name="file size",
                    ),
                ),
                (
                    "referral_answer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        related_query_name="attachment",
                        to="core.ReferralAnswer",
                        verbose_name="referral answer",
                    ),
                ),
            ],
            options={
                "verbose_name": "referral answer attachment",
                "db_table": "partaj_referral_answer_attachment",
            },
        ),
    ]
