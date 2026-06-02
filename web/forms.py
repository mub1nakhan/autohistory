from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from vehicles.models import Vehicle

User = get_user_model()


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vin_code",
            "plate_number",
            "brand",
            "model",
            "year",
            "color",
            "price",
            "currency",
            "fuel_type",
            "transmission",
            "engine_volume",
            "mileage",
            "workshop_visits",
            "is_verified",
            "status",
            "owner",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "workshop_visits": forms.NumberInput(attrs={"min": 0}),
            "is_verified": forms.CheckboxInput(),
            "currency": forms.TextInput(attrs={"placeholder": "USD"}),
            "vin_code": forms.TextInput(attrs={"placeholder": "17-char VIN"}),
            "plate_number": forms.TextInput(attrs={"placeholder": "Plate or registration"}),
            "brand": forms.TextInput(attrs={"placeholder": "Toyota"}),
            "model": forms.TextInput(attrs={"placeholder": "Corolla"}),
            "year": forms.NumberInput(attrs={"min": 1886, "max": 2100}),
            "color": forms.TextInput(attrs={"placeholder": "Blue"}),
        }

    def clean_vin_code(self):
        value = self.cleaned_data["vin_code"].strip().upper()
        if len(value) != 17:
            raise forms.ValidationError("VIN code must be exactly 17 characters.")
        return value


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("Your account is disabled.")
            cleaned_data["user"] = user
        return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
