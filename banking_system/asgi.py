"""
ASGI config for banking_system project.
"""

import os
from django.core.asgi import get_asgi_application
from decouple import config

# Set the settings module based on environment
if config('DJANGO_ENV', default='development') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')

application = get_asgi_application()