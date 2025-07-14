from django.urls import path

from gouthelper_ninja.goutdetails.views import GoutDetailUpdateView

app_name = "goutdetails"

urlpatterns = [
    path("update/<uuid:pk>/", GoutDetailUpdateView.as_view(), name="update"),
]
