"""
WSGI config for freelance_marketplace project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import sys
from django.core.wsgi import get_wsgi_application

# Add the correct paths to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Add the parent directory (freelance_marketplace) to Python path
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PARENT_DIR)

# Add the project root (miniproject) to Python path
PROJECT_ROOT = os.path.dirname(PARENT_DIR)
sys.path.append(PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_marketplace.settings')
application = get_wsgi_application()