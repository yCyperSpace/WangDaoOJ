from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Problem
from .serializers import ProblemSerializer, ProblemUploadSerializer
from .services import build_reference_solution_generator


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
        problem = serializer.save()

        try:
            generator = build_reference_solution_generator()
            problem.reference_solution = generator.generate(problem)
            problem.save(update_fields=["reference_solution"])
        except RuntimeError:
            pass

        return Response(ProblemSerializer(problem).data, status=status.HTTP_201_CREATED)

