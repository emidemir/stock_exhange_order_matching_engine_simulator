import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Create the Celery app instance.
app = Celery('config')

# 3. Configure Celery using settings from Django settings.py.
# We use namespace='CELERY' so we can define settings as CELERY_BROKER_URL, etc.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks in all your installed apps.
# This looks for a 'tasks.py' file in each of your app folders.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run-market-every-5-seconds': {
        'task': 'apps.simulation.tasks.run_simulation_cycle',
        'schedule': 5.0, # Run every 5 seconds
    },
}