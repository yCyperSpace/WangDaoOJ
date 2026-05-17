from django.core.management.base import BaseCommand

from problems.models import Problem, SampleCase, TestCase


class Command(BaseCommand):
    help = "Create a demo problem for local development"

    def handle(self, *args, **options):
        problem, created = Problem.objects.get_or_create(
            title="两数之和",
            defaults={
                "description": "输入两个整数，输出它们的和。",
                "input_description": "一行两个整数 a 和 b。",
                "output_description": "输出 a + b。",
                "difficulty": "easy",
            },
        )
        if created:
            SampleCase.objects.create(problem=problem, input_data="1 2\n", output_data="3\n")
            TestCase.objects.create(problem=problem, input_data="1 2\n", output_data="3\n", is_hidden=False)
        self.stdout.write(self.style.SUCCESS("demo problem ready"))
