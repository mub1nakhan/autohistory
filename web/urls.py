from django.urls import path

from .views import (
    AccidentListView,
    BrowserLoginView,
    BrowserLogoutView,
    BrowserRegisterView,
    HomeView,
    InspectionListView,
    ReportListView,
    RiskScoreListView,
    ServiceRecordListView,
    ProfileView,
    VehicleCreateView,
    VehicleDeleteView,
    VehicleDetailView,
    VehicleListView,
    VehicleUpdateView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", BrowserLoginView.as_view(), name="web-login"),
    path("register/", BrowserRegisterView.as_view(), name="web-register"),
    path("logout/", BrowserLogoutView.as_view(), name="web-logout"),
    path("profile/", ProfileView.as_view(), name="web-profile"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/new/", VehicleCreateView.as_view(), name="vehicle-create"),
    path("vehicles/<uuid:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
    path("vehicles/<uuid:pk>/edit/", VehicleUpdateView.as_view(), name="vehicle-update"),
    path("vehicles/<uuid:pk>/delete/", VehicleDeleteView.as_view(), name="vehicle-delete"),
    path("accidents/", AccidentListView.as_view(), name="accident-list"),
    path("service-records/", ServiceRecordListView.as_view(), name="service-record-list"),
    path("inspections/", InspectionListView.as_view(), name="inspection-list"),
    path("reports/", ReportListView.as_view(), name="report-list"),
    path("risk-scores/", RiskScoreListView.as_view(), name="risk-score-list"),
]
