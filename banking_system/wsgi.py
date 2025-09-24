"""
WSGI config for banking_system project.
"""

import os
from django.core.wsgi import get_wsgi_application
from decouple import config

# Set the settings module based on environment
if config('DJANGO_ENV', default='development') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')

application = get_wsgi_application()

# Apply WSGI middleware for WhiteNoise
if config('DJANGO_ENV', default='development') == 'production':
    from whitenoise import WhiteNoise
    application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))