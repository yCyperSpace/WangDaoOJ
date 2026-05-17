from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("problems", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_code", models.TextField()),
                ("language", models.CharField(default="cpp", max_length=20)),
                (
                    "language_standard",
                    models.CharField(
                        choices=[("c++11", "C++11"), ("c++14", "C++14"), ("c++17", "C++17")],
                        default="c++14",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("wrong_answer", "Wrong Answer"),
                            ("compile_error", "Compile Error"),
                            ("runtime_error", "Runtime Error"),
                            ("time_limit_exceeded", "Time Limit Exceeded"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("detail", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="problems.problem",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
