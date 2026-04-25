WITH vars AS (
    SELECT
        1000::bigint AS property_id,
        NULL::bigint AS source_system_id,
        NULL::bigint AS mapping_id,
        NULL::bigint AS created_by_id,
        NULL::bigint AS updated_by_id
),
src AS (
    SELECT DISTINCT ON (TRIM(s.source_code))
        TRIM(s.source_code) AS code,
        NULLIF(TRIM(s.description), '') AS description,
        NULLIF(TRIM(s.resort), '') AS resort,
        NULLIF(TRIM(s.parent_source_code), '') AS parent_source_code
    FROM stg.origins_of_booking s
    WHERE s.source_code IS NOT NULL
      AND TRIM(s.source_code) <> ''
    ORDER BY TRIM(s.source_code), NULLIF(TRIM(s.description), '') DESC NULLS LAST
),
numbered AS (
    SELECT
        s.code,
        s.description,
        s.resort,
        s.parent_source_code,
        COALESCE((
            SELECT MAX(d.sort_order)
            FROM core.settings_origin_details d
            WHERE d.property_id = (SELECT property_id FROM vars)
        ), 0) + ROW_NUMBER() OVER (ORDER BY s.code) AS new_sort_order
    FROM src s
)
INSERT INTO core.settings_origin_details (
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
    mapping_id,
    property_id,
    source_system_id,
    updated_by_id
)
SELECT
    NOW() AS created_at,
    NOW() AS updated_at,
    TRUE AS is_active,
    n.new_sort_order AS sort_order,
    n.code,
    n.description AS name,
    n.description AS description,
    NULL AS notes,
    NULL AS effective_from,
    NULL AS effective_to,
    TRUE AS is_review_required,
    jsonb_build_object(
        'resort', n.resort,
        'parent_source_code', n.parent_source_code
    ) AS metadata,
    v.created_by_id,
    v.mapping_id,
    v.property_id,
    v.source_system_id,
    v.updated_by_id
FROM numbered n
CROSS JOIN vars v
ON CONFLICT (property_id, code)
DO UPDATE SET
    updated_at = NOW(),
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    source_system_id = COALESCE(EXCLUDED.source_system_id, core.settings_origin_details.source_system_id),
    mapping_id = COALESCE(EXCLUDED.mapping_id, core.settings_origin_details.mapping_id),
    updated_by_id = EXCLUDED.updated_by_id;