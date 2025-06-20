from django.urls import path

from gouthelper_ninja.genders.views import GenderUpdateView

app_name = "genders"

urlpatterns = [
    path("update/<uuid:pk>/", GenderUpdateView.as_view(), name="update"),
]
