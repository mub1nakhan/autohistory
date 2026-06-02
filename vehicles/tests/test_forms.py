from django.test import TestCase
from web.forms import VehicleForm


class VehicleFormTests(TestCase):
    def test_vin_validation(self):
        data = {
            'vin_code': 'SHORTVIN',
            'plate_number': 'ABC123',
            'brand': 'Toyota',
            'model': 'Corolla',
            'year': 2010,
            'color': 'Blue',
            'fuel_type': 'petrol',
            'transmission': 'manual',
            'mileage': 10000,
            'status': 'active'
        }
        form = VehicleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('vin_code', form.errors)