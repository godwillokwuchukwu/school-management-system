from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_profile_teacher_details"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistrationInvitation",
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
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("teacher", "Teacher"),
                            ("student", "Student"),
                            ("parent", "Parent"),
                        ],
                        max_length=20,
                    ),
                ),
                ("token", models.CharField(max_length=64, unique=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registration_invitations",
                        to="auth.user",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
