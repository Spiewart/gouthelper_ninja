from django.urls import path

from gouthelper_ninja.ethnicitys.views import EthnicityUpdateView

app_name = "ethnicitys"

urlpatterns = [
    path("update/<uuid:pk>/", EthnicityUpdateView.as_view(), name="update"),
]
