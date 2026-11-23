USE smart_agriculture_db;

CREATE TABLE IF NOT EXISTS crop_suitability_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_id INT NOT NULL,
    source_record_no INT,
    district VARCHAR(100) NOT NULL,
    upazila VARCHAR(100) NOT NULL,
    season VARCHAR(50) NOT NULL,
    crop_variety VARCHAR(150) NOT NULL,
    crop_characteristic VARCHAR(150),
    very_suitable_area DECIMAL(15,2),
    suitable_area DECIMAL(15,2),
    moderately_suitable_area DECIMAL(15,2),
    marginally_suitable_area DECIMAL(15,2),
    not_suitable_area DECIMAL(15,2),
    area_unit VARCHAR(50),
    source_name VARCHAR(200) NOT NULL,
    source_url VARCHAR(500) NOT NULL,
    source_checked_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crop_id) REFERENCES crops(crop_id),
    UNIQUE KEY unique_source_record (district, upazila, source_record_no)
);

SHOW TABLES;
DESCRIBE crop_suitability_data;

USE smart_agriculture_db;

SELECT crop_id, crop_name
FROM crops
ORDER BY crop_id;

USE smart_agriculture_db;

INSERT INTO crop_suitability_data (
    crop_id,
    source_record_no,
    district,
    upazila,
    season,
    crop_variety,
    crop_characteristic,
    very_suitable_area,
    suitable_area,
    moderately_suitable_area,
    marginally_suitable_area,
    not_suitable_area,
    area_unit,
    source_name,
    source_url,
    source_checked_date
)
VALUES

-- 1. Rice: Boro
(1, NULL, 'Cumilla', 'Debidwar', 'Rabi',
 'Boro Rice', NULL,
 20119, NULL, NULL, NULL, 0,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 2. Rice: Bouna Aus
(1, NULL, 'Cumilla', 'Debidwar', 'Kharif-1',
 'Bouna Aus Rice', NULL,
 4125, NULL, NULL, NULL, 10150,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 3. Rice: Ropa Aus
(1, NULL, 'Cumilla', 'Debidwar', 'Kharif-1',
 'Ropa Aus Rice', NULL,
 4125, NULL, NULL, NULL, 10150,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 4. Rice: Ropa Aman
(1, NULL, 'Cumilla', 'Debidwar', 'Kharif-2',
 'Ropa Aman Rice', NULL,
 4125, NULL, NULL, NULL, 10150,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 5. Rice: Flood tolerant
(1, NULL, 'Cumilla', 'Debidwar', 'Kharif-2',
 'Ropa Aman Rice', 'Flood-tolerant',
 11408, NULL, NULL, NULL, 10150,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 6. Mustard
(3, NULL, 'Cumilla', 'Debidwar', 'Rabi',
 'Mustard', 'অনুকূল পরিবেশ',
 17621, NULL, 3476, 0, 0,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 7. Wheat: Favourable environment
(2, 9, 'Cumilla', 'Debidwar', 'Rabi',
 'Wheat', 'অনুকূল পরিবেশ',
 17621, NULL, 3267, 210, 0,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 8. Wheat: Heat tolerant
(2, 10, 'Cumilla', 'Debidwar', 'Rabi',
 'Wheat', 'তাপ সহনশীল',
 18078, NULL, 3267, 210, 0,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 9. Potato: Favourable environment
(4, 3, 'Cumilla', 'Debidwar', 'Rabi',
 'Potato', 'অনুকূল পরিবেশ',
 17621, NULL, 3267, 210, 0,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11'),

-- 10. Potato: Heat tolerant
(4, 4, 'Cumilla', 'Debidwar', 'Rabi',
 'Potato', 'তাপ সহনশীল',
 0, NULL, 0, 0, 21554,
 NULL, 'BARC Crop Suitability Portal',
 'https://portal.cropzoning.gov.bd/cropSuitability', '2026-11-11');
 
 SELECT
    id,
    crop_id,
    source_record_no,
    district,
    upazila,
    season,
    crop_variety,
    crop_characteristic,
    very_suitable_area,
    suitable_area,
    moderately_suitable_area,
    marginally_suitable_area,
    not_suitable_area
FROM crop_suitability_data
ORDER BY id;

SELECT COUNT(*) AS total_records
FROM crop_suitability_data;