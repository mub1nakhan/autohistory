import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FuelType(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"
    ELECTRIC = "electric", "Electric"
    HYBRID = "hybrid", "Hybrid"
    LPG = "lpg", "LPG"
    CNG = "cng", "CNG"


class TransmissionType(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTOMATIC = "automatic", "Automatic"
    SEMI_AUTO = "semi_auto", "Semi-Automatic"
    CVT = "cvt", "CVT"


class VehicleStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    STOLEN = "stolen", "Stolen"
    WRITTEN_OFF = "written_off", "Written Off"
    SCRAPPED = "scrapped", "Scrapped"


CURRENCY_CHOICES = [
    ("USD", "USD"),
    ("EUR", "EUR"),
    ("GBP", "GBP"),
    ("TRY", "TRY"),
    ("CHF", "CHF"),
]


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vin_code = models.CharField(
        max_length=17, unique=True, db_index=True,
        help_text="17-character Vehicle Identification Number"
    )
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    brand = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    color = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, db_index=True)
    transmission = models.CharField(
        max_length=20, choices=TransmissionType.choices, default=TransmissionType.MANUAL
    )
    engine_volume = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    mileage = models.PositiveIntegerField(default=0, help_text="Current mileage in km")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Suggested price or valuation")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD", help_text="Currency code for the price (e.g. USD, EUR)")
    is_verified = models.BooleanField(default=False, help_text="Is this vehicle record verified by staff?")
    workshop_visits = models.PositiveSmallIntegerField(default=0, help_text="Manual count of workshop visits")
    status = models.CharField(
        max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.ACTIVE, db_index=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_vehicles"
    )
    ownership_count = models.PositiveSmallIntegerField(default=1)
    registered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="registered_vehicles"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["brand", "model"]),
            models.Index(fields=["year"]),
            models.Index(fields=["status"]),
            models.Index(fields=["brand", "model", "year"]),
        ]

    def __str__(self):
        return f"{self.year} {self.brand} {self.model} ({self.vin_code})"

    @property
    def display_name(self):
        return f"{self.year} {self.brand} {self.model}"

    def price_display(self):
        if self.price is None:
            return None
        try:
            return f"{self.currency} {self.price:,.2f}"
        except Exception:
            return f"{self.currency} {self.price}"


class VehicleOwnershipHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="ownership_history")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    owner_name = models.CharField(max_length=200)
    acquired_at = models.DateField()
    released_at = models.DateField(null=True, blank=True)
    transfer_mileage = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_ownership_history"
        ordering = ["-acquired_at"]
        indexes = [
            models.Index(fields=["vehicle", "-acquired_at"]),
        ]

    def __str__(self):
        return f"{self.vehicle.vin_code} → {self.owner_name} ({self.acquired_at})"