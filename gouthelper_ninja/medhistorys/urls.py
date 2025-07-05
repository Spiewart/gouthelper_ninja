from django.urls import path

from gouthelper_ninja.medhistorys.views import MedHistoryCreateView
from gouthelper_ninja.medhistorys.views import MedHistoryUpdateView

app_name = "medhistorys"

urlpatterns = [
    path(
        "<uuid:patient>/create/<str:mhtype>/",
        MedHistoryCreateView.as_view(),
        name="create",
    ),
    path("update/<uuid:pk>/", MedHistoryUpdateView.as_view(), name="update"),
]
