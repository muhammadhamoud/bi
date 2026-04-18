

-- delete from core.settings_segment_details where property_id=1;

----------------------------------------------------------------------------------------------
-- booking_sources and channels
----------------------------------------------------------------------------------------------

WITH vars AS (
    SELECT 1000::bigint AS property_id
)
INSERT INTO core.settings_segment_details (
    created_at,
    updated_at,
    is_active,
    sort_order,
    source_code,
    source_label,
    source_description,
    is_review_required,
    property_id
)
SELECT
    NOW() AS created_at,
    NOW() AS updated_at,
    TRUE AS is_active,
    COALESCE((
        SELECT MAX(d.sort_order)
        FROM core.settings_segment_details d
        WHERE d.property_id = vars.property_id
    ), 0) + ROW_NUMBER() OVER (ORDER BY x.market_code) AS sort_order,
    x.market_code AS source_code,
    x.description AS source_label,
    x.description AS source_description,
    TRUE AS is_review_required,
    vars.property_id AS property_id
FROM (
    SELECT DISTINCT ON (m.market_code)
        m.market_code,
        m.description
    FROM stg.market_codes m
    WHERE m.market_code IS NOT NULL
      AND m.description IS NOT NULL
    ORDER BY m.market_code, m.description
) x
CROSS JOIN vars
JOIN core.settings_segments s
    ON s.property_id = vars.property_id
   AND s.code = x.market_code
WHERE NOT EXISTS (
    SELECT 1
    FROM core.settings_segment_details d
    WHERE d.property_id = vars.property_id
      AND d.source_code = x.market_code
);
