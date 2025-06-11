from django.urls import path

from .views import PatientCreateView
from .views import PatientDetailView
from .views import PatientProviderCreateView
from .views import PatientUpdateView
from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view

app_name = "users"
urlpatterns = [
    path("patients/create/", view=PatientCreateView.as_view(), name="patient-create"),
    path(
        "patients/provider-create/<str:provider>/",
        view=PatientProviderCreateView.as_view(),
        name="provider-patient-create",
    ),
    path(
        "patients/<uuid:patient>/",
        view=PatientDetailView.as_view(),
        name="patient-detail",
    ),
    path(
        "patients/<uuid:patient>/update/",
        view=PatientUpdateView.as_view(),
        name="patient-update",
    ),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
