from django.conf import settings


class DynamicAppRouter:
    """
    Dynamically route apps to databases based on APP_DATABASE_MAPPING.
    Example:
        APP_DATABASE_MAPPING = {
            "settingsmappings": "reports_db",
        }
    """

    def _get_db_for_app(self, app_label):
        return getattr(settings, "APP_DATABASE_MAPPING", {}).get(app_label)

    def db_for_read(self, model, **hints):
        return self._get_db_for_app(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return self._get_db_for_app(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        db1 = self._get_db_for_app(obj1._meta.app_label)
        db2 = self._get_db_for_app(obj2._meta.app_label)

        if db1 and db2:
            return db1 == db2

        if db1 or db2:
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        app_db = self._get_db_for_app(app_label)

        # App is explicitly mapped to a specific database
        if app_db:
            return db == app_db

        # Unmapped apps should only migrate on default
        return db == "default"