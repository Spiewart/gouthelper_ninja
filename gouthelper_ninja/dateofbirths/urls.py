from django.urls import path

from gouthelper_ninja.dateofbirths.views import DateOfBirthUpdateView

app_name = "dateofbirths"

urlpatterns = [
    path("update/<uuid:pk>/", DateOfBirthUpdateView.as_view(), name="update"),
]
