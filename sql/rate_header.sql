WITH vars AS (
    SELECT
        1000::bigint AS property_id,
        NULL::bigint AS source_system_id,
        NULL::bigint AS created_by_id,
        NULL::bigint AS updated_by_id
),
src AS (
    SELECT DISTINCT ON (TRIM(s.rate_code))
        TRIM(s.rate_code) AS code,
        NULLIF(TRIM(s.description), '') AS description,
        NULLIF(TRIM(s.market_code), '') AS market_code,
        NULLIF(TRIM(s.source_code), '') AS source_code
    FROM stg.rate_header s
    WHERE s.rate_code IS NOT NULL
      AND TRIM(s.rate_code) <> ''
    ORDER BY TRIM(s.rate_code), NULLIF(TRIM(s.description), '') DESC NULLS LAST
),
enriched AS (
    SELECT
        s.code,
        s.description,
        s.market_code,
        s.source_code,
        seg.id AS mapping_id,
        org.id AS origin_id
    FROM src s
    CROSS JOIN vars v
    LEFT JOIN core.settings_segment_details seg
        ON seg.property_id = v.property_id
       AND seg.code = s.market_code
    LEFT JOIN core.settings_origin_details org
        ON org.property_id = v.property_id
       AND org.code = s.source_code
),
numbered AS (
    SELECT
        e.code,
        e.description,
        e.market_code,
        e.source_code,
        e.mapping_id,
        e.origin_id,
        COALESCE((
            SELECT MAX(d.sort_order)
            FROM core.settings_rate_code_details d
            WHERE d.property_id = (SELECT property_id FROM vars)
        ), 0) + ROW_NUMBER() OVER (ORDER BY e.code) AS new_sort_order
    FROM enriched e
)
INSERT INTO core.settings_rate_code_details (
    created_at,
    updated_at,
    is_active,
    sort_order,
    code,
    name,
    description,
    notes,
    effective_from,
    effective_to,
    is_review_required,
    metadata,
    created_by_id,
    property_id,
    source_system_id,
    updated_by_id,
    origin_id,
    mapping_id
)
SELECT
    NOW() AS created_at,
    NOW() AS updated_at,
    TRUE AS is_active,
    n.new_sort_order AS sort_order,
    n.code,
    COALESCE(n.description, n.code) AS name,
    n.description AS description,
    NULL AS notes,
    NULL AS effective_from,
    NULL AS effective_to,
    TRUE AS is_review_required,
    jsonb_build_object(
        'market_code', n.market_code,
        'source_code', n.source_code
    ) AS metadata,
    v.created_by_id,
    v.property_id,
    v.source_system_id,
    v.updated_by_id,
    n.origin_id,
    n.mapping_id
FROM numbered n
CROSS JOIN vars v
ON CONFLICT (property_id, code)
DO UPDATE SET
    updated_at = NOW(),
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    source_system_id = COALESCE(EXCLUDED.source_system_id, core.settings_rate_code_details.source_system_id),
    mapping_id = COALESCE(EXCLUDED.mapping_id, core.settings_rate_code_details.mapping_id),
    origin_id = COALESCE(EXCLUDED.origin_id, core.settings_rate_code_details.origin_id),
    updated_by_id = EXCLUDED.updated_by_id;