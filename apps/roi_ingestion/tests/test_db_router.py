from apps.roi_ingestion.db_router import RoiStagingRouter
from apps.roi_ingestion.models import RoiReservationDailyStage, RoiReservationStage


def test_database_router_routes_staging_models_to_roi_staging():
    router = RoiStagingRouter()
    assert router.db_for_read(RoiReservationStage) == "roi_staging"
    assert router.db_for_write(RoiReservationDailyStage) == "roi_staging"
    assert router.allow_migrate("roi_staging", "roi_ingestion", "roireservationstage") is True
    assert router.allow_migrate("default", "roi_ingestion", "roireservationstage") is False
