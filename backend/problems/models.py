from django.db import models


class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_description = models.TextField(blank=True)
    output_description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, default="medium")
    reference_solution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class SampleCase(models.Model):
    problem = models.ForeignKey(Problem, related_name="sample_cases", on_delete=models.CASCADE)
    input_data = models.TextField()
    output_data = models.TextField()


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, related_name="test_cases", on_delete=models.CASCADE)
    input_data = models.TextField()
    output_data = models.TextField()
    is_hidden = models.BooleanField(default=True)

