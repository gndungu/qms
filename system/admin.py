from django.contrib import admin
from django.apps import apps
from django.utils.module_loading import import_string
from django.contrib.admin.sites import AlreadyRegistered

# Optional: Add models you don't want to auto-register
IGNORED_MODELS = [
    # 'AppName.ModelName',
    # 'myapp.SecretModel',
]

app = apps.get_app_config(__name__.split('.')[-2])

for model in app.get_models():
    model_identifier = f"{model._meta.app_label}.{model.__name__}"
    if model_identifier in IGNORED_MODELS:
        continue

    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
