from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DeleteView, DetailView, FormView, ListView, TemplateView

from accidents.models import Accident
from inspections.models import Inspection
from reports.models import Report
from risk_engine.models import RiskScore
from service_records.models import ServiceRecord
from vehicles.models import Vehicle
from vehicles.services import VehicleService
from .forms import LoginForm, RegisterForm, VehicleForm


class HomeView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = {
            "vehicles": Vehicle.objects.count(),
            "accidents": Accident.objects.count(),
            "service_records": ServiceRecord.objects.count(),
            "inspections": Inspection.objects.count(),
            "reports": Report.objects.count(),
            "risk_scores": RiskScore.objects.count(),
        }
        context["recent_vehicles"] = (
            Vehicle.objects.select_related("owner")
            .annotate(
                accident_count=Count("accidents", distinct=True),
                service_record_count=Count("service_records", distinct=True),
            )
            .order_by("-created_at")[:6]
        )
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "web/auth/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_profile"] = user
        context["recent_login_history"] = user.login_history.all()[:10]
        return context


class BrowserLoginView(FormView):
    template_name = "web/auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        auth_login(self.request, form.cleaned_data["user"])
        messages.success(self.request, "Welcome back.")
        return super().form_valid(form)


class BrowserRegisterView(FormView):
    template_name = "web/auth/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        messages.success(self.request, "Account created successfully.")
        return super().form_valid(form)


class BrowserLogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, "You have been signed out.")
        return redirect("home")

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, "You have been signed out.")
        return redirect("home")


class VehicleListView(ListView):
    template_name = "web/vehicles/list.html"
    model = Vehicle
    context_object_name = "vehicles"
    paginate_by = 12

    def get_queryset(self):
        queryset = Vehicle.objects.select_related("owner", "registered_by").order_by("-created_at")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(vin_code__icontains=query)
                | Q(plate_number__icontains=query)
                | Q(brand__icontains=query)
                | Q(model__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class VehicleCreateView(LoginRequiredMixin, TemplateView):
    template_name = "web/vehicles/form.html"
    form_class = VehicleForm
    mode = "create"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") or self.form_class()
        context["mode"] = self.mode
        context["title"] = "Add Vehicle"
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            vehicle = VehicleService.create_vehicle(
                data=form.cleaned_data,
                registered_by=request.user if request.user.is_authenticated else None,
            )
            return self._redirect_success(vehicle)
        return self.render_to_response(self.get_context_data(form=form))

    def _redirect_success(self, vehicle):
        from django.shortcuts import redirect

        return redirect("vehicle-detail", pk=vehicle.pk)


class VehicleUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "web/vehicles/form.html"
    form_class = VehicleForm
    mode = "update"

    def dispatch(self, request, *args, **kwargs):
        self.vehicle = get_object_or_404(Vehicle, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        context["form"] = kwargs.get("form") or self.form_class(instance=self.vehicle)
        context["mode"] = self.mode
        context["title"] = f"Edit {self.vehicle.display_name}"
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.vehicle)
        if form.is_valid():
            vehicle = VehicleService.update_vehicle(self.vehicle, form.cleaned_data)
            return self._redirect_success(vehicle)
        return self.render_to_response(self.get_context_data(form=form))

    def _redirect_success(self, vehicle):
        from django.shortcuts import redirect

        return redirect("vehicle-detail", pk=vehicle.pk)


class VehicleDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicle
    template_name = "web/vehicles/delete_confirm.html"
    success_url = reverse_lazy("vehicle-list")

    def get_queryset(self):
        return Vehicle.objects.select_related("owner", "registered_by")


class VehicleDetailView(DetailView):
    template_name = "web/vehicles/detail.html"
    model = Vehicle
    context_object_name = "vehicle"

    def get_queryset(self):
        return (
            Vehicle.objects.select_related("owner", "registered_by")
            .prefetch_related("accidents", "service_records", "inspections", "ownership_history")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.object
        context["summary"] = VehicleService.get_vehicle_summary(vehicle)
        try:
            context["risk_score"] = vehicle.risk_score
        except ObjectDoesNotExist:
            context["risk_score"] = None
        context["accidents"] = vehicle.accidents.all()
        context["service_records"] = vehicle.service_records.all()
        context["inspections"] = vehicle.inspections.all()
        context["ownership_history"] = vehicle.ownership_history.all()
        return context


class AccidentListView(ListView):
    template_name = "web/records/accidents.html"
    model = Accident
    context_object_name = "accidents"
    paginate_by = 12

    def get_queryset(self):
        return Accident.objects.select_related("vehicle", "created_by", "verified_by").order_by("-accident_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = Accident.objects.count()
        context["verified"] = Accident.objects.filter(verified=True).count()
        context["high_severity"] = Accident.objects.filter(severity="high").count()
        return context


class ServiceRecordListView(ListView):
    template_name = "web/records/service_records.html"
    model = ServiceRecord
    context_object_name = "service_records"
    paginate_by = 12

    def get_queryset(self):
        return ServiceRecord.objects.select_related("vehicle", "created_by").order_by("-service_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = ServiceRecord.objects.count()
        context["recent"] = ServiceRecord.objects.order_by("-service_date")[:5]
        return context


class InspectionListView(ListView):
    template_name = "web/records/inspections.html"
    model = Inspection
    context_object_name = "inspections"
    paginate_by = 12

    def get_queryset(self):
        return Inspection.objects.select_related("vehicle", "inspector").order_by("-inspection_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = Inspection.objects.count()
        context["passed"] = Inspection.objects.filter(result="passed").count()
        context["failed"] = Inspection.objects.filter(result="failed").count()
        return context


class ReportListView(ListView):
    template_name = "web/records/reports.html"
    model = Report
    context_object_name = "reports"
    paginate_by = 12

    def get_queryset(self):
        return Report.objects.select_related("vehicle").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = Report.objects.count()
        return context


class RiskScoreListView(ListView):
    template_name = "web/records/risk_scores.html"
    model = RiskScore
    context_object_name = "risk_scores"
    paginate_by = 12

    def get_queryset(self):
        return RiskScore.objects.select_related("vehicle").order_by("-last_calculated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = RiskScore.objects.count()
        context["high_risk"] = RiskScore.objects.filter(risk_score__gte=70).count()
        context["medium_risk"] = RiskScore.objects.filter(risk_score__gte=40, risk_score__lt=70).count()
        return context
