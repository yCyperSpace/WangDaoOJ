from django.contrib import admin

from .models import Problem, SampleCase, TestCase


class SampleCaseInline(admin.TabularInline):
    model = SampleCase
    extra = 1


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "difficulty", "created_at"]
    search_fields = ["title"]
    inlines = [SampleCaseInline, TestCaseInline]

