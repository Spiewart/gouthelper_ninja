from django.urls import path

from .views import PatientCreateView
from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view

app_name = "users"
urlpatterns = [
    path("patients/create/", view=PatientCreateView.as_view(), name="patient-create"),
    path(
        "patients/provider-create/<str:provider>/",
        view=PatientCreateView.as_view(),
        name="provider-patient-create",
    ),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
