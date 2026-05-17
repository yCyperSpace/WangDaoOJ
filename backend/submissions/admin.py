from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "problem", "language", "status", "created_at"]
    list_filter = ["status", "language"]

