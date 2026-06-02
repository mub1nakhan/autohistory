import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
import sys
import pathlib
# ensure project root is on sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import django
django.setup()
from django.urls import reverse
print('vehicle-list ->', reverse('vehicle-list'))
try:
    print('api-vehicle-list ->', reverse('api-vehicle-list'))
except Exception as e:
    print('api-vehicle-list reverse error', e)
