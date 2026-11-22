"""
MyMedicine — PythonAnywhere WSGI Configuration
Replace 'yourusername' with your actual PythonAnywhere username.
Paste the contents of this file into your PythonAnywhere WSGI config.
"""
import sys
import os

path = '/home/yourusername/MyMedicine'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mymedicine.settings'
os.environ['DEBUG'] = 'False'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
