from rest_framework import serializers

from .models import Problem, SampleCase, TestCase


class SampleCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCase
        fields = ["id", "input_data", "output_data"]


class TestCaseUploadSerializer(serializers.Serializer):
    input_data = serializers.CharField()
    output_data = serializers.CharField()


class ProblemSerializer(serializers.ModelSerializer):
    sample_cases = SampleCaseSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "input_description",
            "output_description",
            "difficulty",
            "sample_cases",
            "created_at",
        ]


class ProblemUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    input_description = serializers.CharField(required=False, allow_blank=True)
    output_description = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.CharField(required=False, default="medium")
    samples = TestCaseUploadSerializer(many=True)

    def create(self, validated_data):
        samples = validated_data.pop("samples")
        problem = Problem.objects.create(**validated_data)
        for sample in samples:
            SampleCase.objects.create(problem=problem, **sample)
            TestCase.objects.create(problem=problem, is_hidden=False, **sample)
        return problem

