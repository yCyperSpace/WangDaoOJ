from django.db import models

from problems.models import Problem


class Submission(models.Model):
    class LanguageStandard(models.TextChoices):
        CPP11 = "c++11", "C++11"
        CPP14 = "c++14", "C++14"
        CPP17 = "c++17", "C++17"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        WRONG_ANSWER = "wrong_answer", "Wrong Answer"
        COMPILE_ERROR = "compile_error", "Compile Error"
        RUNTIME_ERROR = "runtime_error", "Runtime Error"
        TIME_LIMIT_EXCEEDED = "time_limit_exceeded", "Time Limit Exceeded"

    problem = models.ForeignKey(Problem, related_name="submissions", on_delete=models.CASCADE)
    source_code = models.TextField()
    language = models.CharField(max_length=20, default="cpp")
    language_standard = models.CharField(
        max_length=10,
        choices=LanguageStandard.choices,
        default=LanguageStandard.CPP14,
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
