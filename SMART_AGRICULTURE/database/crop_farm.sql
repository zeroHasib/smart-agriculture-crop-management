SELECT
    id,
    crop_id,
    source_record_no,
    district,
    upazila,
    crop_variety
FROM crop_suitability_data;

ALTER TABLE crop_suitability_data
DROP INDEX unique_source_record;

ALTER TABLE crop_suitability_data
ADD UNIQUE KEY unique_source_record (
    district,
    upazila,
    source_record_no,
    crop_id
);

SELECT COUNT(*) AS total_records
FROM crop_suitability_data;

SELECT
    c.crop_name,
    COUNT(*) AS total_records
FROM crop_suitability_data cs
JOIN crops c
    ON cs.crop_id = c.crop_id
GROUP BY c.crop_name
ORDER BY c.crop_name;

USE smart_agriculture_db;

UPDATE farms
SET
    latitude = 23.60,
    longitude = 90.98
WHERE farm_id = 2;
SELECT
    farm_id,
    farm_name,
    district,
    latitude,
    longitude
FROM farms
WHERE farm_id = 2;

USE smart_agriculture_db;

UPDATE farms
SET
    latitude = 23.60,
    longitude = 90.98
WHERE farmer_id = 5;
SELECT
    farm_id,
    farmer_id,
    farm_name,
    district,
    latitude,
    longitude
FROM farms
WHERE farmer_id = 5;


USE smart_agriculture_db;

UPDATE farms
SET
    latitude = CASE
        WHEN LOWER(TRIM(district)) = 'dhaka'
            THEN 23.8103
        WHEN LOWER(TRIM(district)) = 'cumilla'
            THEN 23.4607
        ELSE latitude
    END,

    longitude = CASE
        WHEN LOWER(TRIM(district)) = 'dhaka'
            THEN 90.4125
        WHEN LOWER(TRIM(district)) = 'cumilla'
            THEN 91.1809
        ELSE longitude
    END

WHERE farmer_id = 5;
SELECT
    farm_id,
    farm_name,
    district,
    latitude,
    longitude
FROM farms
WHERE farmer_id = 5
ORDER BY farm_id;

SELECT farm_id, farm_name, district, latitude, longitude
FROM farms
WHERE farmer_id = 5
ORDER BY farm_id;