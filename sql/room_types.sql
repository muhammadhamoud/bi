-- DELETE FROM core.settings_room_type_details;

WITH vars AS (
    SELECT
        1000::bigint AS property_id,
        NULL::bigint AS source_system_id,
        NULL::bigint AS mapping_id,
        NULL::bigint AS created_by_id,
        NULL::bigint AS updated_by_id
),
src AS (
    SELECT DISTINCT ON (s.resort, s.room_category)
        s.resort,
        s.room_category,
        TRIM(s.label) AS code,
        TRIM(s.short_description) AS short_description,
        TRIM(s.room_class) AS room_class,
        s.number_rooms AS number_of_rooms
    FROM stg.room_category s
    WHERE s.room_category > 0
      AND s.label IS NOT NULL
      AND TRIM(s.label) <> ''
    ORDER BY s.resort, s.room_category, TRIM(s.label)
),
numbered AS (
    SELECT
        s.code,
        s.short_description,
        s.number_of_rooms,
        s.room_category,
        s.room_class,
        COALESCE((
            SELECT MAX(d.sort_order)
            FROM core.settings_room_type_details d
            WHERE d.property_id = (SELECT property_id FROM vars)
        ), 0) + ROW_NUMBER() OVER (ORDER BY s.room_category, s.code) AS new_sort_order
    FROM src s
)
INSERT INTO core.settings_room_type_details (
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
    updated_by_id,
    number_of_rooms,
    room_category,
    room_class
)
SELECT
    NOW() AS created_at,
    NOW() AS updated_at,
    TRUE AS is_active,
    n.new_sort_order AS sort_order,
    n.code,
    n.short_description AS name,
    n.short_description AS description,
    NULL AS notes,
    NULL AS effective_from,
    NULL AS effective_to,
    TRUE AS is_review_required,
    '{}'::jsonb AS metadata,
    v.created_by_id,
    v.mapping_id,
    v.property_id,
    v.source_system_id,
    v.updated_by_id,
    n.number_of_rooms,
    n.room_category,
    n.room_class
FROM numbered n
CROSS JOIN vars v
ON CONFLICT (property_id, code)
DO UPDATE SET
    updated_at = NOW(),
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    source_system_id = COALESCE(EXCLUDED.source_system_id, core.settings_room_type_details.source_system_id),
    mapping_id = COALESCE(EXCLUDED.mapping_id, core.settings_room_type_details.mapping_id),
    updated_by_id = EXCLUDED.updated_by_id,
    number_of_rooms = EXCLUDED.number_of_rooms,
    room_category = EXCLUDED.room_category,
    room_class = EXCLUDED.room_class;