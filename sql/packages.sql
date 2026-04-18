-- SELECT resort
-- , product
-- , description
-- , product_type
-- , currency_code
-- , calculation_rule
-- , print_separate_yn
-- , add_to_rate_yn
-- , dept_code
-- , dept_tax_flag
-- , forecast_next_day_yn
-- , forecast_group_code
-- , insert_date
-- , update_date
-- FROM stg.resort_products;


WITH vars AS (
    SELECT
        1000::bigint AS property_id,
        NULL::bigint AS source_system_id,
        NULL::bigint AS mapping_id,
        NULL::bigint AS created_by_id,
        NULL::bigint AS updated_by_id
),
src AS (
    SELECT DISTINCT ON (s.resort, TRIM(s.product))
        s.resort,
        TRIM(s.product) AS code,
        TRIM(s.description) AS description,
        TRIM(s.product_type) AS product_type,
        TRIM(s.currency_code) AS currency_code,
        TRIM(s.calculation_rule) AS calculation_rule,
        s.print_separate_yn,
        s.add_to_rate_yn,
        TRIM(s.dept_code) AS dept_code,
        TRIM(s.dept_tax_flag) AS dept_tax_flag,
        s.forecast_next_day_yn,
        TRIM(s.forecast_group_code) AS forecast_group_code,
        s.insert_date,
        s.update_date
    FROM stg.resort_products s
    WHERE s.product IS NOT NULL
      AND TRIM(s.product) <> ''
    ORDER BY s.resort, TRIM(s.product), s.update_date DESC NULLS LAST, s.insert_date DESC NULLS LAST
),
numbered AS (
    SELECT
        s.code,
        s.description,
        s.product_type,
        s.currency_code,
        s.calculation_rule,
        s.print_separate_yn,
        s.add_to_rate_yn,
        s.dept_code,
        s.dept_tax_flag,
        s.forecast_next_day_yn,
        s.forecast_group_code,
        s.insert_date,
        s.update_date,
        COALESCE((
            SELECT MAX(d.sort_order)
            FROM core.settings_package_details d
            WHERE d.property_id = (SELECT property_id FROM vars)
        ), 0) + ROW_NUMBER() OVER (ORDER BY s.code) AS new_sort_order
    FROM src s
)
INSERT INTO core.settings_package_details (
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
    jsonb_strip_nulls(
        jsonb_build_object(
            'product_type', n.product_type,
            'currency_code', n.currency_code,
            'calculation_rule', n.calculation_rule,
            'print_separate_yn', n.print_separate_yn,
            'add_to_rate_yn', n.add_to_rate_yn,
            'dept_code', n.dept_code,
            'dept_tax_flag', n.dept_tax_flag,
            'forecast_next_day_yn', n.forecast_next_day_yn,
            'forecast_group_code', n.forecast_group_code,
            'source_insert_date', n.insert_date,
            'source_update_date', n.update_date
        )
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
    source_system_id = COALESCE(EXCLUDED.source_system_id, core.settings_package_details.source_system_id),
    mapping_id = COALESCE(EXCLUDED.mapping_id, core.settings_package_details.mapping_id),
    updated_by_id = EXCLUDED.updated_by_id;