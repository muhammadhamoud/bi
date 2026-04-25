def map_fields_to_headers(fields: list[str], headers: list[str]) -> dict:
    values = {}
    for index, header in enumerate(headers):
        values[header] = fields[index] if index < len(fields) else None
    if len(fields) > len(headers):
        values["_extra"] = fields[len(headers):]
    return values


def parse_pipe_record(raw: str, headers: list[str]) -> dict:
    return map_fields_to_headers(raw.split("|"), headers)


def parse_compound_records(raw: str | None, headers: list[str]) -> list[dict]:
    if raw is None:
        return []
    value = raw.strip()
    if value in {"", "{#", "{{#", "#"}:
        return []

    while value.endswith("#"):
        value = value[:-1]
    while value.endswith("{"):
        value = value[:-1]

    records: list[dict] = []
    for sequence_no, part in enumerate(segment for segment in value.split("{") if segment != ""):
        fields = part.split("|")
        records.append(
            {
                "sequence_no": sequence_no,
                "raw": part,
                "values": map_fields_to_headers(fields, headers),
            }
        )
    return records
