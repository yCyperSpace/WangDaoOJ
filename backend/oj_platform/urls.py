from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/problems/", include("problems.urls")),
    path("api/submissions/", include("submissions.urls")),
]

