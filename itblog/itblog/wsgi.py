import os
from os.path import abspath, dirname
from sys import path
 
SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)
path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'itblog'))
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iitblog.settings")
 
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
