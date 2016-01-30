"""
WSGI config for jorvik project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import newrelic.agent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jorvik.settings")

# New Relic Agent (env: NEW_RELIC_CONFIG_FILE)
newrelic.agent.initialize()

from django.core.wsgi import get_wsgi_application
application = newrelic.agent.wsgi_application()(get_wsgi_application())
