from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Problem, SampleCase, TestCase
from .serializers import ProblemSerializer, ProblemUploadSerializer
from .services import build_problem_package_generator


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.prefetch_related("sample_cases").all()
    serializer_class = ProblemSerializer

    def get_serializer_class(self):
        if self.action == "upload":
            return ProblemUploadSerializer
        return ProblemSerializer

    @action(detail=False, methods=["post"])
    def upload(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        statement = serializer.validated_data["statement"]

        generator = build_problem_package_generator()
        package = generator.generate(statement)
        problem = Problem.objects.create(
            title=package["title"],
            description=package["description"],
            input_description=package["input_description"],
            output_description=package["output_description"],
            difficulty=package["difficulty"],
            reference_solution=package["reference_solution"],
        )
        for sample in package["sample_cases"]:
            SampleCase.objects.create(problem=problem, **sample)
            TestCase.objects.create(problem=problem, is_hidden=False, **sample)
        for test_case in package["hidden_test_cases"]:
            TestCase.objects.create(problem=problem, is_hidden=True, **test_case)

        return Response(ProblemSerializer(problem).data, status=status.HTTP_201_CREATED)
