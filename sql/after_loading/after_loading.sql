CREATE OR REPLACE VIEW data.v_roi_reservation_clean AS
SELECT
    id AS reservation_stage_id,
    file_record_id,
    property_id,
    source_system_code,
    file_name,
    property_code,
    snapshot_name,
    snapshot_date,
    business_date,
    resort,
    currency_code,
    integration_id,
    arrival_date,
    status AS reservation_status,
    reservation_id,

    NULLIF(details_json ->> 'name_id', '') AS name_id,
    NULLIF(details_json ->> 'membership_id', '') AS membership_id,

    CASE 
        WHEN NULLIF(details_json ->> 'business_date_created', '') IS NOT NULL
        THEN (details_json ->> 'business_date_created')::date
        ELSE NULL
    END AS business_date_created,

    CASE 
        WHEN NULLIF(details_json ->> 'trunc_end_date', '') IS NOT NULL
        THEN (details_json ->> 'trunc_end_date')::date
        ELSE NULL
    END AS trunc_end_date,

    CASE 
        WHEN NULLIF(details_json ->> 'insert_date', '') IS NOT NULL
        THEN (details_json ->> 'insert_date')::timestamp
        ELSE NULL
    END AS insert_date,

    CASE 
        WHEN NULLIF(details_json ->> 'update_date', '') IS NOT NULL
        THEN (details_json ->> 'update_date')::timestamp
        ELSE NULL
    END AS update_date,

    CASE 
        WHEN NULLIF(details_json ->> 'cancellation_date', '') IS NOT NULL
        THEN (details_json ->> 'cancellation_date')::timestamp
        ELSE NULL
    END AS cancellation_date,

    NULLIF(details_json ->> 'confirmation_no', '') AS confirmation_no,
    NULLIF(details_json ->> 'cancellation_reason_code', '') AS cancellation_reason_code,
    NULLIF(details_json ->> 'channel', '') AS channel,
    NULLIF(details_json ->> 'country', '') AS country,
    NULLIF(details_json ->> 'state', '') AS state,
    NULLIF(details_json ->> 'city', '') AS city,
    NULLIF(details_json ->> 'guarantee_code', '') AS guarantee_code,
    NULLIF(details_json ->> 'guarantee_code_pre_ci', '') AS guarantee_code_pre_ci,
    NULLIF(details_json ->> 'payment_method', '') AS payment_method,
    NULLIF(details_json ->> 'purpose_of_stay', '') AS purpose_of_stay,

    CASE 
        WHEN NULLIF(details_json ->> 'commission_paid', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (details_json ->> 'commission_paid')::numeric
        ELSE NULL
    END AS commission_paid,

    NULLIF(details_json ->> 'commission_payout_to', '') AS commission_payout_to,
    NULLIF(details_json ->> 'gender', '') AS gender,
    NULLIF(details_json ->> 'nationality', '') AS nationality,
    NULLIF(details_json ->> 'title', '') AS title,

    row_hash,
    created_at
FROM data.roi_reservation_stage;


CREATE OR REPLACE VIEW data.v_roi_daily_rden_accounts AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE 
        WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer
        ELSE NULL
    END AS day_offset,

    NULLIF(parsed_values ->> 'resv_daily_el_seq', '') AS resv_daily_el_seq,

    CASE 
        WHEN NULLIF(parsed_values ->> 'reservation_date', '') IS NOT NULL
        THEN (parsed_values ->> 'reservation_date')::date
        ELSE NULL
    END AS reservation_date,

    NULLIF(parsed_values ->> 'company', '') AS company,
    NULLIF(parsed_values ->> 'company_id', '') AS company_id,
    NULLIF(parsed_values ->> 'travel_agent', '') AS travel_agent,
    NULLIF(parsed_values ->> 'travel_agent_code', '') AS travel_agent_code,
    NULLIF(parsed_values ->> 'industry_code', '') AS industry_code,
    NULLIF(parsed_values ->> 'source', '') AS source,
    NULLIF(parsed_values ->> 'source_code', '') AS source_code,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RDEN_ACCOUNTS';

CREATE OR REPLACE VIEW data.v_roi_daily_rden_codes AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE 
        WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer
        ELSE NULL
    END AS day_offset,

    NULLIF(parsed_values ->> 'rate_code', '') AS rate_code,
    NULLIF(parsed_values ->> 'currency_code', '') AS currency_code,

    CASE 
        WHEN NULLIF(parsed_values ->> 'adults', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'adults')::integer
        ELSE NULL
    END AS adults,

    CASE 
        WHEN NULLIF(parsed_values ->> 'children', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'children')::integer
        ELSE NULL
    END AS children,

    CASE 
        WHEN NULLIF(parsed_values ->> 'share_amount', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'share_amount')::numeric
        ELSE NULL
    END AS share_amount,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RDEN_CODES';

CREATE OR REPLACE VIEW data.v_roi_daily_market_channel AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE 
        WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer
        ELSE NULL
    END AS day_offset,

    NULLIF(parsed_values ->> 'allotment_header_id', '') AS allotment_header_id,
    NULLIF(parsed_values ->> 'resv_daily_el_seq', '') AS resv_daily_el_seq,

    CASE 
        WHEN NULLIF(parsed_values ->> 'reservation_date', '') IS NOT NULL
        THEN (parsed_values ->> 'reservation_date')::date
        ELSE NULL
    END AS reservation_date,

    NULLIF(parsed_values ->> 'market_code', '') AS market_code,
    NULLIF(parsed_values ->> 'origin_of_booking', '') AS origin_of_booking,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RDE_MARKET_CHANNEL';


CREATE OR REPLACE VIEW data.v_roi_daily_categories AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE 
        WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer
        ELSE NULL
    END AS day_offset,

    NULLIF(parsed_values ->> 'room', '') AS room,
    NULLIF(parsed_values ->> 'room_category', '') AS room_category,
    NULLIF(parsed_values ->> 'booked_room_category', '') AS booked_room_category,
    NULLIF(parsed_values ->> 'room_class', '') AS room_class,
    NULLIF(parsed_values ->> 'day_use_yn', '') AS day_use_yn,
    NULLIF(parsed_values ->> 'due_out_yn', '') AS due_out_yn,

    CASE 
        WHEN NULLIF(parsed_values ->> 'rate_amount', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'rate_amount')::numeric
        ELSE NULL
    END AS rate_amount,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RDE_CATEGORIES';

CREATE OR REPLACE VIEW data.v_roi_daily_res_stat_1 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    NULLIF(parsed_values ->> 'allotment_header_id', '') AS allotment_header_id,

    CASE WHEN NULLIF(parsed_values ->> 'business_date', '') IS NOT NULL
        THEN (parsed_values ->> 'business_date')::date ELSE NULL END AS business_date,

    CASE WHEN NULLIF(parsed_values ->> 'arr_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'arr_rooms')::numeric ELSE NULL END AS arr_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'dep_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'dep_rooms')::numeric ELSE NULL END AS dep_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'adults', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'adults')::integer ELSE NULL END AS adults,

    CASE WHEN NULLIF(parsed_values ->> 'children', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'children')::integer ELSE NULL END AS children,

    CASE WHEN NULLIF(parsed_values ->> 'nights', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'nights')::numeric ELSE NULL END AS nights,

    CASE WHEN NULLIF(parsed_values ->> 'single_occupancy', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'single_occupancy')::numeric ELSE NULL END AS single_occupancy,

    CASE WHEN NULLIF(parsed_values ->> 'room_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'room_revenue')::numeric ELSE NULL END AS room_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'food_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'food_revenue')::numeric ELSE NULL END AS food_revenue,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_STAT_1';


CREATE OR REPLACE VIEW data.v_roi_daily_res_stat_2 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    CASE WHEN NULLIF(parsed_values ->> 'other_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'other_revenue')::numeric ELSE NULL END AS other_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'non_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'non_revenue')::numeric ELSE NULL END AS non_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'total_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_revenue')::numeric ELSE NULL END AS total_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'room_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'room_revenue_tax')::numeric ELSE NULL END AS room_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'food_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'food_revenue_tax')::numeric ELSE NULL END AS food_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'other_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'other_revenue_tax')::numeric ELSE NULL END AS other_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'non_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'non_revenue_tax')::numeric ELSE NULL END AS non_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'total_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_revenue_tax')::numeric ELSE NULL END AS total_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'fc_room_revenue_ratio', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'fc_room_revenue_ratio')::numeric ELSE NULL END AS fc_room_revenue_ratio,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_STAT_2';

CREATE OR REPLACE VIEW data.v_roi_daily_res_stat_3 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    CASE WHEN NULLIF(parsed_values ->> 'day_use_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'day_use_rooms')::numeric ELSE NULL END AS day_use_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'package_food_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'package_food_revenue')::numeric ELSE NULL END AS package_food_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'total_package_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_package_revenue')::numeric ELSE NULL END AS total_package_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'cancelled_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'cancelled_rooms')::numeric ELSE NULL END AS cancelled_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'no_show_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'no_show_rooms')::numeric ELSE NULL END AS no_show_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'no_of_stays', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'no_of_stays')::numeric ELSE NULL END AS no_of_stays,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_STAT_3';


CREATE OR REPLACE VIEW data.v_roi_daily_res_stat AS
SELECT
    s1.daily_stage_id,
    s1.file_record_id,
    s1.property_id,
    s1.reservation_stage_id,
    s1.reservation_row_hash,
    s1.source_system_code,
    s1.file_name,
    s1.property_code,
    s1.snapshot_date,
    s1.reservation_id,
    s1.sequence_no,
    s1.day_offset,
    s1.allotment_header_id,
    s1.business_date,

    s1.arr_rooms,
    s1.dep_rooms,
    s1.adults,
    s1.children,
    s1.nights,
    s1.single_occupancy,
    s1.room_revenue,
    s1.food_revenue,

    s2.other_revenue,
    s2.non_revenue,
    s2.total_revenue,
    s2.room_revenue_tax,
    s2.food_revenue_tax,
    s2.other_revenue_tax,
    s2.non_revenue_tax,
    s2.total_revenue_tax,
    s2.fc_room_revenue_ratio,

    s3.day_use_rooms,
    s3.package_food_revenue,
    s3.total_package_revenue,
    s3.cancelled_rooms,
    s3.no_show_rooms,
    s3.no_of_stays,

    s1.raw_record AS stat_1_raw_record,
    s2.raw_record AS stat_2_raw_record,
    s3.raw_record AS stat_3_raw_record,

    s1.row_hash AS stat_1_row_hash,
    s2.row_hash AS stat_2_row_hash,
    s3.row_hash AS stat_3_row_hash,

    s1.created_at
FROM data.v_roi_daily_res_stat_1 s1
LEFT JOIN data.v_roi_daily_res_stat_2 s2
    ON s2.file_record_id = s1.file_record_id
   AND s2.reservation_id = s1.reservation_id
   AND s2.sequence_no = s1.sequence_no
LEFT JOIN data.v_roi_daily_res_stat_3 s3
    ON s3.file_record_id = s1.file_record_id
   AND s3.reservation_id = s1.reservation_id
   AND s3.sequence_no = s1.sequence_no;


CREATE OR REPLACE VIEW data.v_roi_daily_res_summary_1 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    NULLIF(parsed_values ->> 'allotment_header_id', '') AS allotment_header_id,

    CASE WHEN NULLIF(parsed_values ->> 'business_date', '') IS NOT NULL
        THEN (parsed_values ->> 'business_date')::date ELSE NULL END AS business_date,

    CASE WHEN NULLIF(parsed_values ->> 'arr_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'arr_rooms')::numeric ELSE NULL END AS arr_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'dep_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'dep_rooms')::numeric ELSE NULL END AS dep_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'adults', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'adults')::integer ELSE NULL END AS adults,

    CASE WHEN NULLIF(parsed_values ->> 'children', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'children')::integer ELSE NULL END AS children,

    CASE WHEN NULLIF(parsed_values ->> 'no_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'no_rooms')::numeric ELSE NULL END AS no_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'single_occupancy', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'single_occupancy')::numeric ELSE NULL END AS single_occupancy,

    CASE WHEN NULLIF(parsed_values ->> 'room_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'room_revenue')::numeric ELSE NULL END AS room_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'food_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'food_revenue')::numeric ELSE NULL END AS food_revenue,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_SUMMARY_1';

CREATE OR REPLACE VIEW data.v_roi_daily_res_summary_2 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    CASE WHEN NULLIF(parsed_values ->> 'other_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'other_revenue')::numeric ELSE NULL END AS other_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'non_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'non_revenue')::numeric ELSE NULL END AS non_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'total_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_revenue')::numeric ELSE NULL END AS total_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'room_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'room_revenue_tax')::numeric ELSE NULL END AS room_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'food_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'food_revenue_tax')::numeric ELSE NULL END AS food_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'other_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'other_revenue_tax')::numeric ELSE NULL END AS other_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'non_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'non_revenue_tax')::numeric ELSE NULL END AS non_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'total_revenue_tax', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_revenue_tax')::numeric ELSE NULL END AS total_revenue_tax,

    CASE WHEN NULLIF(parsed_values ->> 'fc_room_revenue_ratio', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'fc_room_revenue_ratio')::numeric ELSE NULL END AS fc_room_revenue_ratio,

    CASE WHEN NULLIF(parsed_values ->> 'day_use_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'day_use_rooms')::numeric ELSE NULL END AS day_use_rooms,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_SUMMARY_2';


CREATE OR REPLACE VIEW data.v_roi_daily_res_summary_3 AS
SELECT
    id AS daily_stage_id,
    file_record_id,
    property_id,
    reservation_stage_id,
    reservation_row_hash,
    source_system_code,
    file_name,
    property_code,
    snapshot_date,
    reservation_id,
    sequence_no,

    CASE WHEN NULLIF(parsed_values ->> 'day_offset', '') ~ '^-?[0-9]+$'
        THEN (parsed_values ->> 'day_offset')::integer ELSE NULL END AS day_offset,

    CASE WHEN NULLIF(parsed_values ->> 'package_food_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'package_food_revenue')::numeric ELSE NULL END AS package_food_revenue,

    CASE WHEN NULLIF(parsed_values ->> 'total_package_revenue', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'total_package_revenue')::numeric ELSE NULL END AS total_package_revenue,

    NULLIF(parsed_values ->> 'booking_status', '') AS booking_status,
    NULLIF(parsed_values ->> 'block_status', '') AS block_status,

    CASE WHEN NULLIF(parsed_values ->> 'remaining_block_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'remaining_block_rooms')::numeric ELSE NULL END AS remaining_block_rooms,

    CASE WHEN NULLIF(parsed_values ->> 'pickedup_block_rooms', '') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN (parsed_values ->> 'pickedup_block_rooms')::numeric ELSE NULL END AS pickedup_block_rooms,

    raw_record,
    row_hash,
    created_at
FROM data.roi_reservation_daily_stage
WHERE detail_type = 'RES_SUMMARY_3';



CREATE OR REPLACE VIEW data.v_roi_daily_res_summary AS
SELECT
    s1.daily_stage_id,
    s1.file_record_id,
    s1.property_id,
    s1.reservation_stage_id,
    s1.reservation_row_hash,
    s1.source_system_code,
    s1.file_name,
    s1.property_code,
    s1.snapshot_date,
    s1.reservation_id,
    s1.sequence_no,
    s1.day_offset,
    s1.allotment_header_id,
    s1.business_date,

    s1.arr_rooms,
    s1.dep_rooms,
    s1.adults,
    s1.children,
    s1.no_rooms,
    s1.single_occupancy,
    s1.room_revenue,
    s1.food_revenue,

    s2.other_revenue,
    s2.non_revenue,
    s2.total_revenue,
    s2.room_revenue_tax,
    s2.food_revenue_tax,
    s2.other_revenue_tax,
    s2.non_revenue_tax,
    s2.total_revenue_tax,
    s2.fc_room_revenue_ratio,
    s2.day_use_rooms,

    s3.package_food_revenue,
    s3.total_package_revenue,
    s3.booking_status,
    s3.block_status,
    s3.remaining_block_rooms,
    s3.pickedup_block_rooms,

    s1.raw_record AS summary_1_raw_record,
    s2.raw_record AS summary_2_raw_record,
    s3.raw_record AS summary_3_raw_record,

    s1.row_hash AS summary_1_row_hash,
    s2.row_hash AS summary_2_row_hash,
    s3.row_hash AS summary_3_row_hash,

    s1.created_at
FROM data.v_roi_daily_res_summary_1 s1
LEFT JOIN data.v_roi_daily_res_summary_2 s2
    ON s2.file_record_id = s1.file_record_id
   AND s2.reservation_id = s1.reservation_id
   AND s2.sequence_no = s1.sequence_no
LEFT JOIN data.v_roi_daily_res_summary_3 s3
    ON s3.file_record_id = s1.file_record_id
   AND s3.reservation_id = s1.reservation_id
   AND s3.sequence_no = s1.sequence_no;


DROP VIEW IF EXISTS data.v_roi_daily_res_summary CASCADE;

CREATE VIEW data.v_roi_daily_res_summary AS
WITH summary_keys AS (
    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_summary_1

    UNION

    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_summary_2

    UNION

    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_summary_3
)

SELECT
    COALESCE(s1.daily_stage_id, s2.daily_stage_id, s3.daily_stage_id) AS daily_stage_id,
    k.file_record_id,
    COALESCE(s1.property_id, s2.property_id, s3.property_id) AS property_id,
    COALESCE(s1.reservation_stage_id, s2.reservation_stage_id, s3.reservation_stage_id) AS reservation_stage_id,
    COALESCE(s1.reservation_row_hash, s2.reservation_row_hash, s3.reservation_row_hash) AS reservation_row_hash,
    COALESCE(s1.source_system_code, s2.source_system_code, s3.source_system_code) AS source_system_code,
    COALESCE(s1.file_name, s2.file_name, s3.file_name) AS file_name,
    COALESCE(s1.property_code, s2.property_code, s3.property_code) AS property_code,
    COALESCE(s1.snapshot_date, s2.snapshot_date, s3.snapshot_date) AS snapshot_date,

    k.reservation_id,
    k.sequence_no,

    COALESCE(s1.day_offset, s2.day_offset, s3.day_offset) AS day_offset,

    s1.allotment_header_id,
    s1.business_date,

    s1.arr_rooms,
    s1.dep_rooms,
    s1.adults,
    s1.children,
    s1.no_rooms,
    s1.single_occupancy,
    s1.room_revenue,
    s1.food_revenue,

    s2.other_revenue,
    s2.non_revenue,
    s2.total_revenue,
    s2.room_revenue_tax,
    s2.food_revenue_tax,
    s2.other_revenue_tax,
    s2.non_revenue_tax,
    s2.total_revenue_tax,
    s2.fc_room_revenue_ratio,
    s2.day_use_rooms,

    s3.package_food_revenue,
    s3.total_package_revenue,
    s3.booking_status,
    s3.block_status,
    s3.remaining_block_rooms,
    s3.pickedup_block_rooms,

    s1.raw_record AS summary_1_raw_record,
    s2.raw_record AS summary_2_raw_record,
    s3.raw_record AS summary_3_raw_record,

    s1.row_hash AS summary_1_row_hash,
    s2.row_hash AS summary_2_row_hash,
    s3.row_hash AS summary_3_row_hash,

    COALESCE(s1.created_at, s2.created_at, s3.created_at) AS created_at

FROM summary_keys k

LEFT JOIN data.v_roi_daily_res_summary_1 s1
    ON s1.file_record_id = k.file_record_id
   AND s1.reservation_id = k.reservation_id
   AND s1.sequence_no = k.sequence_no

LEFT JOIN data.v_roi_daily_res_summary_2 s2
    ON s2.file_record_id = k.file_record_id
   AND s2.reservation_id = k.reservation_id
   AND s2.sequence_no = k.sequence_no

LEFT JOIN data.v_roi_daily_res_summary_3 s3
    ON s3.file_record_id = k.file_record_id
   AND s3.reservation_id = k.reservation_id
   AND s3.sequence_no = k.sequence_no;



   DROP VIEW IF EXISTS data.v_roi_daily_res_stat CASCADE;

CREATE VIEW data.v_roi_daily_res_stat AS
WITH stat_keys AS (
    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_stat_1

    UNION

    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_stat_2

    UNION

    SELECT DISTINCT file_record_id, reservation_id, sequence_no
    FROM data.v_roi_daily_res_stat_3
)

SELECT
    COALESCE(s1.daily_stage_id, s2.daily_stage_id, s3.daily_stage_id) AS daily_stage_id,
    k.file_record_id,
    COALESCE(s1.property_id, s2.property_id, s3.property_id) AS property_id,
    COALESCE(s1.reservation_stage_id, s2.reservation_stage_id, s3.reservation_stage_id) AS reservation_stage_id,
    COALESCE(s1.reservation_row_hash, s2.reservation_row_hash, s3.reservation_row_hash) AS reservation_row_hash,
    COALESCE(s1.source_system_code, s2.source_system_code, s3.source_system_code) AS source_system_code,
    COALESCE(s1.file_name, s2.file_name, s3.file_name) AS file_name,
    COALESCE(s1.property_code, s2.property_code, s3.property_code) AS property_code,
    COALESCE(s1.snapshot_date, s2.snapshot_date, s3.snapshot_date) AS snapshot_date,

    k.reservation_id,
    k.sequence_no,

    COALESCE(s1.day_offset, s2.day_offset, s3.day_offset) AS day_offset,

    s1.allotment_header_id,
    s1.business_date,

    s1.arr_rooms,
    s1.dep_rooms,
    s1.adults,
    s1.children,
    s1.nights,
    s1.single_occupancy,
    s1.room_revenue,
    s1.food_revenue,

    s2.other_revenue,
    s2.non_revenue,
    s2.total_revenue,
    s2.room_revenue_tax,
    s2.food_revenue_tax,
    s2.other_revenue_tax,
    s2.non_revenue_tax,
    s2.total_revenue_tax,
    s2.fc_room_revenue_ratio,

    s3.day_use_rooms,
    s3.package_food_revenue,
    s3.total_package_revenue,
    s3.cancelled_rooms,
    s3.no_show_rooms,
    s3.no_of_stays,

    s1.raw_record AS stat_1_raw_record,
    s2.raw_record AS stat_2_raw_record,
    s3.raw_record AS stat_3_raw_record,

    s1.row_hash AS stat_1_row_hash,
    s2.row_hash AS stat_2_row_hash,
    s3.row_hash AS stat_3_row_hash,

    COALESCE(s1.created_at, s2.created_at, s3.created_at) AS created_at

FROM stat_keys k

LEFT JOIN data.v_roi_daily_res_stat_1 s1
    ON s1.file_record_id = k.file_record_id
   AND s1.reservation_id = k.reservation_id
   AND s1.sequence_no = k.sequence_no

LEFT JOIN data.v_roi_daily_res_stat_2 s2
    ON s2.file_record_id = k.file_record_id
   AND s2.reservation_id = k.reservation_id
   AND s2.sequence_no = k.sequence_no

LEFT JOIN data.v_roi_daily_res_stat_3 s3
    ON s3.file_record_id = k.file_record_id
   AND s3.reservation_id = k.reservation_id
   AND s3.sequence_no = k.sequence_no;










DROP VIEW IF EXISTS data.v_roi_daily_flat CASCADE;

CREATE VIEW data.v_roi_daily_flat AS
WITH daily_keys AS (
    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_rden_accounts
    WHERE day_offset IS NOT NULL

    UNION

    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_rden_codes
    WHERE day_offset IS NOT NULL

    UNION

    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_market_channel
    WHERE day_offset IS NOT NULL

    UNION

    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_categories
    WHERE day_offset IS NOT NULL

    UNION

    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_res_summary
    WHERE day_offset IS NOT NULL

    UNION

    SELECT DISTINCT file_record_id, reservation_id, day_offset
    FROM data.v_roi_daily_res_stat
    WHERE day_offset IS NOT NULL
),

base AS (
    SELECT
        r.reservation_stage_id,
        r.file_record_id,
        r.property_id,
        r.source_system_code,
        r.file_name,
        r.property_code,
        r.snapshot_name,
        r.snapshot_date,
        r.business_date AS snapshot_business_date,
        r.resort,
        r.currency_code AS reservation_currency_code,
        r.integration_id,
        r.reservation_id,
        r.confirmation_no,
        r.name_id,
        r.membership_id,
        r.arrival_date,
        r.trunc_end_date,
        r.business_date_created,
        r.insert_date,
        r.update_date,
        r.cancellation_date,
        r.reservation_status,
        r.cancellation_reason_code,
        r.channel,
        r.country,
        r.state,
        r.city,
        r.guarantee_code,
        r.guarantee_code_pre_ci,
        r.payment_method,
        r.purpose_of_stay,
        r.commission_paid,
        r.commission_payout_to,
        r.gender,
        r.nationality,
        r.title,

        k.day_offset,

        COALESCE(
            st.sequence_no,
            sm.sequence_no,
            a.sequence_no,
            c.sequence_no,
            m.sequence_no,
            cat.sequence_no
        ) AS sequence_no,

        COALESCE(
            st.business_date,
            sm.business_date,
            a.reservation_date,
            m.reservation_date
        ) AS reservation_date,

        a.resv_daily_el_seq AS account_resv_daily_el_seq,
        a.company,
        a.company_id,
        a.travel_agent,
        a.travel_agent_code,
        a.industry_code,
        a.source,
        a.source_code,

        c.rate_code,
        c.currency_code AS rate_currency_code,
        c.adults AS rate_adults,
        c.children AS rate_children,
        c.share_amount,

        m.allotment_header_id AS market_allotment_header_id,
        m.resv_daily_el_seq AS market_resv_daily_el_seq,
        m.market_code,
        m.origin_of_booking,

        cat.room,
        cat.room_category,
        cat.booked_room_category,
        cat.room_class,
        cat.day_use_yn,
        cat.due_out_yn,
        cat.rate_amount,

        sm.allotment_header_id AS summary_allotment_header_id,
        sm.business_date AS summary_business_date,
        sm.arr_rooms AS summary_arr_rooms,
        sm.dep_rooms AS summary_dep_rooms,
        sm.adults AS summary_adults,
        sm.children AS summary_children,
        sm.no_rooms AS summary_no_rooms,
        sm.single_occupancy AS summary_single_occupancy,
        sm.room_revenue AS summary_room_revenue,
        sm.food_revenue AS summary_food_revenue,
        sm.other_revenue AS summary_other_revenue,
        sm.non_revenue AS summary_non_revenue,
        sm.total_revenue AS summary_total_revenue,
        sm.room_revenue_tax AS summary_room_revenue_tax,
        sm.food_revenue_tax AS summary_food_revenue_tax,
        sm.other_revenue_tax AS summary_other_revenue_tax,
        sm.non_revenue_tax AS summary_non_revenue_tax,
        sm.total_revenue_tax AS summary_total_revenue_tax,
        sm.fc_room_revenue_ratio AS summary_fc_room_revenue_ratio,
        sm.day_use_rooms AS summary_day_use_rooms,
        sm.package_food_revenue AS summary_package_food_revenue,
        sm.total_package_revenue AS summary_total_package_revenue,
        sm.booking_status AS summary_booking_status,
        sm.block_status AS summary_block_status,
        sm.remaining_block_rooms AS summary_remaining_block_rooms,
        sm.pickedup_block_rooms AS summary_pickedup_block_rooms,

        st.allotment_header_id AS stat_allotment_header_id,
        st.business_date AS stat_business_date,
        st.arr_rooms AS stat_arr_rooms,
        st.dep_rooms AS stat_dep_rooms,
        st.adults AS stat_adults,
        st.children AS stat_children,
        st.nights AS stat_nights,
        st.single_occupancy AS stat_single_occupancy,
        st.room_revenue AS stat_room_revenue,
        st.food_revenue AS stat_food_revenue,
        st.other_revenue AS stat_other_revenue,
        st.non_revenue AS stat_non_revenue,
        st.total_revenue AS stat_total_revenue,
        st.room_revenue_tax AS stat_room_revenue_tax,
        st.food_revenue_tax AS stat_food_revenue_tax,
        st.other_revenue_tax AS stat_other_revenue_tax,
        st.non_revenue_tax AS stat_non_revenue_tax,
        st.total_revenue_tax AS stat_total_revenue_tax,
        st.fc_room_revenue_ratio AS stat_fc_room_revenue_ratio,
        st.day_use_rooms AS stat_day_use_rooms,
        st.package_food_revenue AS stat_package_food_revenue,
        st.total_package_revenue AS stat_total_package_revenue,
        st.cancelled_rooms AS stat_cancelled_rooms,
        st.no_show_rooms AS stat_no_show_rooms,
        st.no_of_stays AS stat_no_of_stays

    FROM data.v_roi_reservation_clean r

    LEFT JOIN daily_keys k
        ON k.file_record_id = r.file_record_id
       AND k.reservation_id = r.reservation_id

    LEFT JOIN data.v_roi_daily_rden_accounts a
        ON a.file_record_id = k.file_record_id
       AND a.reservation_id = k.reservation_id
       AND a.day_offset = k.day_offset

    LEFT JOIN data.v_roi_daily_rden_codes c
        ON c.file_record_id = k.file_record_id
       AND c.reservation_id = k.reservation_id
       AND c.day_offset = k.day_offset

    LEFT JOIN data.v_roi_daily_market_channel m
        ON m.file_record_id = k.file_record_id
       AND m.reservation_id = k.reservation_id
       AND m.day_offset = k.day_offset

    LEFT JOIN data.v_roi_daily_categories cat
        ON cat.file_record_id = k.file_record_id
       AND cat.reservation_id = k.reservation_id
       AND cat.day_offset = k.day_offset

    LEFT JOIN data.v_roi_daily_res_summary sm
        ON sm.file_record_id = k.file_record_id
       AND sm.reservation_id = k.reservation_id
       AND sm.day_offset = k.day_offset

    LEFT JOIN data.v_roi_daily_res_stat st
        ON st.file_record_id = k.file_record_id
       AND st.reservation_id = k.reservation_id
       AND st.day_offset = k.day_offset
)

SELECT
    reservation_stage_id,
    file_record_id,
    property_id,
    source_system_code,
    file_name,
    property_code,
    snapshot_name,
    snapshot_date,
    snapshot_business_date,
    resort,
    reservation_currency_code,
    integration_id,
    reservation_id,
    confirmation_no,
    name_id,
    membership_id,
    arrival_date,
    trunc_end_date,
    business_date_created,
    insert_date,
    update_date,
    cancellation_date,
    reservation_status,
    cancellation_reason_code,
    channel,
    country,
    state,
    city,
    guarantee_code,
    guarantee_code_pre_ci,
    payment_method,
    purpose_of_stay,
    commission_paid,
    commission_payout_to,
    gender,
    nationality,
    title,

    sequence_no,
    day_offset,
    reservation_date,

    account_resv_daily_el_seq,
    company,
    company_id,
    travel_agent,
    travel_agent_code,
    industry_code,
    source,
    source_code,

    rate_code,
    rate_currency_code,
    share_amount,

    market_allotment_header_id,
    market_resv_daily_el_seq,
    market_code,
    origin_of_booking,

    room,
    room_category,
    booked_room_category,
    room_class,
    day_use_yn,
    due_out_yn,
    rate_amount,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_allotment_header_id, stat_allotment_header_id)
        ELSE COALESCE(stat_allotment_header_id, summary_allotment_header_id)
    END AS allotment_header_id,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_business_date, stat_business_date)
        ELSE COALESCE(stat_business_date, summary_business_date)
    END AS business_date,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_arr_rooms, stat_arr_rooms)
        ELSE COALESCE(stat_arr_rooms, summary_arr_rooms)
    END AS arr_rooms,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_dep_rooms, stat_dep_rooms)
        ELSE COALESCE(stat_dep_rooms, summary_dep_rooms)
    END AS dep_rooms,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_adults, stat_adults, rate_adults)
        ELSE COALESCE(stat_adults, summary_adults, rate_adults)
    END AS adults,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_children, stat_children, rate_children)
        ELSE COALESCE(stat_children, summary_children, rate_children)
    END AS children,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_no_rooms, stat_nights)
        ELSE COALESCE(stat_nights, summary_no_rooms)
    END AS nights,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_single_occupancy, stat_single_occupancy)
        ELSE COALESCE(stat_single_occupancy, summary_single_occupancy)
    END AS single_occupancy,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_room_revenue, stat_room_revenue)
        ELSE COALESCE(stat_room_revenue, summary_room_revenue)
    END AS room_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_food_revenue, stat_food_revenue)
        ELSE COALESCE(stat_food_revenue, summary_food_revenue)
    END AS food_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_other_revenue, stat_other_revenue)
        ELSE COALESCE(stat_other_revenue, summary_other_revenue)
    END AS other_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_non_revenue, stat_non_revenue)
        ELSE COALESCE(stat_non_revenue, summary_non_revenue)
    END AS non_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_total_revenue, stat_total_revenue)
        ELSE COALESCE(stat_total_revenue, summary_total_revenue)
    END AS total_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_room_revenue_tax, stat_room_revenue_tax)
        ELSE COALESCE(stat_room_revenue_tax, summary_room_revenue_tax)
    END AS room_revenue_tax,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_food_revenue_tax, stat_food_revenue_tax)
        ELSE COALESCE(stat_food_revenue_tax, summary_food_revenue_tax)
    END AS food_revenue_tax,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_other_revenue_tax, stat_other_revenue_tax)
        ELSE COALESCE(stat_other_revenue_tax, summary_other_revenue_tax)
    END AS other_revenue_tax,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_non_revenue_tax, stat_non_revenue_tax)
        ELSE COALESCE(stat_non_revenue_tax, summary_non_revenue_tax)
    END AS non_revenue_tax,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_total_revenue_tax, stat_total_revenue_tax)
        ELSE COALESCE(stat_total_revenue_tax, summary_total_revenue_tax)
    END AS total_revenue_tax,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_fc_room_revenue_ratio, stat_fc_room_revenue_ratio)
        ELSE COALESCE(stat_fc_room_revenue_ratio, summary_fc_room_revenue_ratio)
    END AS fc_room_revenue_ratio,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_day_use_rooms, stat_day_use_rooms)
        ELSE COALESCE(stat_day_use_rooms, summary_day_use_rooms)
    END AS day_use_rooms,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_package_food_revenue, stat_package_food_revenue)
        ELSE COALESCE(stat_package_food_revenue, summary_package_food_revenue)
    END AS package_food_revenue,

    CASE
        WHEN reservation_date > snapshot_date
            THEN COALESCE(summary_total_package_revenue, stat_total_package_revenue)
        ELSE COALESCE(stat_total_package_revenue, summary_total_package_revenue)
    END AS total_package_revenue,

    stat_cancelled_rooms AS cancelled_rooms,
    stat_no_show_rooms AS no_show_rooms,
    stat_no_of_stays AS no_of_stays,

    summary_booking_status AS booking_status,
    summary_block_status AS block_status,
    summary_remaining_block_rooms AS remaining_block_rooms,
    summary_pickedup_block_rooms AS pickedup_block_rooms

FROM base;







SELECT
    detail_type,
    reservation_id,
    sequence_no,
    parsed_values ->> 'day_offset' AS day_offset,
    parsed_values ->> 'business_date' AS business_date,
    parsed_values ->> 'reservation_date' AS reservation_date,
    raw_record
FROM data.roi_reservation_daily_stage
WHERE reservation_id = (
    SELECT reservation_id
    FROM data.roi_reservation_daily_stage
    WHERE detail_type LIKE 'RES_SUMMARY_%'
    LIMIT 1
)
AND detail_type IN (
    'RDEN_ACCOUNTS',
    'RDEN_CODES',
    'RDE_MARKET_CHANNEL',
    'RDE_CATEGORIES',
    'RES_SUMMARY_1',
    'RES_SUMMARY_2',
    'RES_SUMMARY_3',
    'RES_STAT_1',
    'RES_STAT_2',
    'RES_STAT_3'
)
ORDER BY reservation_id, detail_type, sequence_no;