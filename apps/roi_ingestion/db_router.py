class RoiStagingRouter:
    staging_app_label = "roi_ingestion"
    staging_model_names = {"roireservationstage", "roireservationdailystage"}
    staging_db_alias = "roi_staging"

    def _is_staging_model(self, model) -> bool:
        return (
            model._meta.app_label == self.staging_app_label
            and model._meta.model_name in self.staging_model_names
        )

    def db_for_read(self, model, **hints):
        if self._is_staging_model(model):
            return self.staging_db_alias
        return None

    def db_for_write(self, model, **hints):
        if self._is_staging_model(model):
            return self.staging_db_alias
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        normalized_model_name = (model_name or "").lower()
        if app_label == self.staging_app_label and normalized_model_name in self.staging_model_names:
            return db == self.staging_db_alias
        if db == self.staging_db_alias:
            return False
        return None
