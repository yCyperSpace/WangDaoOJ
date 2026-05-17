from rest_framework import serializers

from .models import Problem, SampleCase


class SampleCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCase
        fields = ["id", "input_data", "output_data"]


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
    statement = serializers.CharField()
