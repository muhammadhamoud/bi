from datetime import date

import pytest

from apps.roi_ingestion.services.roi_xml_parser import RoiFileContext, RoiXmlParser, RoiXmlParserError
from .sample_xml import SAMPLE_XML


def test_xml_parser_small_sample(tmp_path):
    path = tmp_path / "ROI_DAILY_DXBJV_20260422.XML"
    path.write_text(SAMPLE_XML)
    context = RoiFileContext("ROI_DAILY_DXBJV_20260422.XML", "ROI_DAILY", "DXBJV", date(2026, 4, 22), "XML")
    parsed = list(RoiXmlParser().parse(path, context))
    assert len(parsed) == 1
    assert parsed[0].reservation_id == "50059"
    assert parsed[0].business_date == date(2026, 4, 22)
    assert len(parsed[0].daily_details) == 4


def test_xml_parser_invalid_root(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text("<BAD></BAD>")
    context = RoiFileContext("bad.xml", "ROI_DAILY", "DXBJV", date(2026, 4, 22), "XML")
    with pytest.raises(RoiXmlParserError):
        list(RoiXmlParser().parse(path, context))
