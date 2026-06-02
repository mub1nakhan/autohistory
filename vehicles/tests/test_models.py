from django.test import TestCase
from vehicles.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()


class VehicleModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', first_name='Test', last_name='User')

    def test_price_display_formats_currency(self):
        v = Vehicle.objects.create(
            vin_code='1HGCM82633A004352',
            plate_number='ABC1234',
            brand='Toyota',
            model='Corolla',
            year=2010,
            color='Blue',
            fuel_type='petrol',
            transmission='manual',
            mileage=50000,
            price=1234.56,
            currency='USD',
            owner=self.user,
        )
        self.assertEqual(v.price_display(), 'USD 1,234.56')