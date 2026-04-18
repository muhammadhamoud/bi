

----------------------------------------------------------------------------------------------
-- booking_sources and channels
----------------------------------------------------------------------------------------------

WITH vars AS (
    SELECT
        1000::bigint AS property_id,
        NULL::bigint AS source_system_id,
        NULL::bigint AS category_id,
        NULL::bigint AS created_by_id,
        NULL::bigint AS updated_by_id
),
src AS (
    SELECT DISTINCT ON (UPPER(TRIM(c.attribute_code)))
        UPPER(TRIM(c.attribute_code)) AS code,
        TRIM(c.description) AS label
    FROM stg.channel_codes c
    WHERE c.attribute_code IS NOT NULL
      AND TRIM(c.attribute_code) <> ''
      AND c.description IS NOT NULL
      AND TRIM(c.description) <> ''
    ORDER BY UPPER(TRIM(c.attribute_code)), TRIM(c.description)
),
numbered AS (
    SELECT
        s.code,
        s.label,
        COALESCE((
            SELECT MAX(b.sort_order)
            FROM core.settings_booking_sources b
            WHERE b.property_id = (SELECT property_id FROM vars)
        ), 0) + ROW_NUMBER() OVER (ORDER BY s.code) AS new_sort_order
    FROM src s
)
INSERT INTO core.settings_booking_sources (
    created_at,
    updated_at,
    is_active,
    sort_order,
    code,
    name,
    description,
    notes,
    is_review_required,
    effective_from,
    effective_to,
    metadata,
    created_by_id,
    property_id,
    source_system_id,
    updated_by_id,
    category_id
)
SELECT
    NOW() AS created_at,
    NOW() AS updated_at,
    TRUE AS is_active,
    n.new_sort_order AS sort_order,
    n.code,
    n.label AS name,
    n.label AS description,
    NULL AS notes,
    TRUE AS is_review_required,
    NULL AS effective_from,
    NULL AS effective_to,
    '{}'::jsonb AS metadata,
    v.created_by_id,
    v.property_id,
    v.source_system_id,
    v.updated_by_id,
    v.category_id
FROM numbered n
CROSS JOIN vars v
ON CONFLICT (property_id, code)
DO UPDATE SET
    updated_at = NOW(),
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    source_system_id = COALESCE(EXCLUDED.source_system_id, core.settings_booking_sources.source_system_id),
    category_id = COALESCE(EXCLUDED.category_id, core.settings_booking_sources.category_id),
    updated_by_id = EXCLUDED.updated_by_id;

