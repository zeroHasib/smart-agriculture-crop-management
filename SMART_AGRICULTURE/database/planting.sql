USE smart_agriculture_db;
CREATE TABLE IF NOT EXISTS planting_cycles (
    cycle_id INT AUTO_INCREMENT PRIMARY KEY,
    field_id INT NOT NULL,
    crop_id INT NOT NULL,
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    status VARCHAR(30) DEFAULT 'Growing',

    FOREIGN KEY (field_id)
        REFERENCES fields(field_id),

    FOREIGN KEY (crop_id)
        REFERENCES crops(crop_id)
);

USE smart_agriculture_db;

SHOW TABLES;

DESCRIBE planting_cycles;


USE smart_agriculture_db;

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    cycle_id INT NOT NULL,
    expense_type VARCHAR(100) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (cycle_id)
        REFERENCES planting_cycles(cycle_id),

    CHECK (amount >= 0)
);

USE smart_agriculture_db;

DESCRIBE expenses;


USE smart_agriculture_db;

CREATE TABLE IF NOT EXISTS harvests (
    harvest_id INT AUTO_INCREMENT PRIMARY KEY,
    cycle_id INT NOT NULL,
    harvest_date DATE NOT NULL,
    harvested_quantity_kg DECIMAL(10,2) NOT NULL,
    sold_quantity_kg DECIMAL(10,2) DEFAULT 0.00,
    price_per_kg DECIMAL(10,2) NOT NULL,
    description TEXT,

    FOREIGN KEY (cycle_id)
        REFERENCES planting_cycles(cycle_id),

    CHECK (harvested_quantity_kg > 0),
    CHECK (sold_quantity_kg >= 0),
    CHECK (sold_quantity_kg <= harvested_quantity_kg),
    CHECK (price_per_kg >= 0)
);

USE smart_agriculture_db;

DESCRIBE harvests;

USE smart_agriculture_db;

-- 1. Check crops table
DESCRIBE crops;

-- 2. Check fields table
DESCRIBE fields;

-- 3. Check farms table
DESCRIBE farms;

-- 4. Check existing crops
SELECT * FROM crops;

-- 5. Check your farms and fields
SELECT
    farms.farm_id,
    farms.farm_name,
    farms.district,
    farms.latitude,
    farms.longitude,
    fields.field_id,
    fields.field_name,
    fields.soil_type,
    fields.soil_ph
FROM farms
INNER JOIN fields
ON farms.farm_id = fields.farm_id
ORDER BY farms.farm_id;

USE smart_agriculture_db;

DESCRIBE crops;

SELECT * FROM crops;

DESCRIBE farms;

DESCRIBE crops;

SELECT * FROM crops;

USE smart_agriculture_db;

UPDATE farms
SET district = 'Cumilla'
WHERE farm_id = 2
AND farmer_id = 5;

SELECT farm_id, farm_name, district
FROM farms
WHERE farm_id = 2;

USE smart_agriculture_db;

CREATE TABLE IF NOT EXISTS crop_recommendation_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,

    crop_id INT NOT NULL,

    district VARCHAR(100) NOT NULL,
    upazila VARCHAR(100) NOT NULL,

    season VARCHAR(50) NOT NULL,

    crop_variety VARCHAR(100),

    suitability_class ENUM(
        'Very Suitable',
        'Suitable',
        'Moderately Suitable',
        'Marginally Suitable',
        'Not Suitable'
    ) NOT NULL,

    recommendation_note TEXT,

    source_name VARCHAR(200) NOT NULL,
    source_url VARCHAR(500) NOT NULL,
    source_checked_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (crop_id)
        REFERENCES crops(crop_id),

    UNIQUE KEY unique_crop_location_season (
        crop_id,
        district,
        upazila,
        season
    )
);
DESCRIBE crop_recommendation_rules;

USE smart_agriculture_db;

SHOW TABLES;

DESCRIBE crop_suitability_data;

USE smart_agriculture_db;

CREATE TABLE crop_suitability_data (
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

    UNIQUE KEY unique_source_record (
        district, upazila, source_record_no
    )
);

DESCRIBE crop_suitability_data;