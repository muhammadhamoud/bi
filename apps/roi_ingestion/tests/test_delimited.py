from apps.roi_ingestion.constants import RESERVATION_DETAILS_HEADERS
from apps.roi_ingestion.utils.delimited import map_fields_to_headers, parse_compound_records, parse_pipe_record


def test_parse_compound_records_rden_accounts():
    raw = "0|199192|2024-11-01|FAZAA||AFFILIATE PHG/US|68350066|||"
    records = parse_compound_records(raw, ["day_offset", "resv_daily_el_seq", "reservation_date", "company", "company_id", "travel_agent", "travel_agent_code", "industry_code", "source", "source_code"])
    assert records[0]["sequence_no"] == 0
    assert records[0]["values"]["company_id"] == ""
    assert records[0]["values"]["source_code"] == ""


def test_parse_compound_records_trailing_double_open_hash():
    raw = "0|17IQB0|AED|2|0|400{1|17IQB0|AED|2|0|400{{#"
    records = parse_compound_records(raw, ["day_offset", "rate_code", "currency_code", "adults", "children", "share_amount"])
    assert len(records) == 2
    assert records[1]["values"]["rate_code"] == "17IQB0"


def test_map_fields_to_headers_missing_fields():
    mapped = map_fields_to_headers(["a"], ["one", "two"])
    assert mapped == {"one": "a", "two": None}


def test_map_fields_to_headers_extra_fields():
    mapped = map_fields_to_headers(["a", "b", "c"], ["one"])
    assert mapped == {"one": "a", "_extra": ["b", "c"]}


def test_reservation_details_parsing():
    raw = "49122||2024-10-07|2024-11-02|2024-10-08 03:18:22"
    mapped = parse_pipe_record(raw, RESERVATION_DETAILS_HEADERS)
    assert mapped["name_id"] == "49122"
    assert mapped["membership_id"] == ""
    assert mapped["trunc_end_date"] == "2024-11-02"
