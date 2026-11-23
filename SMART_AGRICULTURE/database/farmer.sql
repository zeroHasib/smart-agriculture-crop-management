
USE smart_agriculture_db;

SELECT farmer_id, full_name, email, phone
FROM farmers;


USE smart_agriculture_db;

SELECT farmer_id, full_name, email, password_hash
FROM farmers
WHERE email = 'tj123@gmail.com';


USE smart_agriculture_db;

SELECT
    farms.farm_id,
    farms.farm_name,
    farms.farmer_id,
    farmers.full_name
FROM farms
INNER JOIN farmers
ON farms.farmer_id = farmers.farmer_id;

SELECT
    fields.field_id,
    fields.field_name,
    farms.farm_id,
    farms.farmer_id
FROM fields
INNER JOIN farms
ON fields.farm_id = farms.farm_id;

USE smart_agriculture_db;

SELECT
    farms.farm_id,
    farms.farm_name,
    farms.farmer_id,
    farmers.full_name,
    farmers.email
FROM farms
INNER JOIN farmers
ON farms.farmer_id = farmers.farmer_id;

SELECT * FROM farms;
SELECT *
FROM farms
WHERE farmer_id = 5;

USE smart_agriculture_db;

SELECT farmer_id, full_name, email
FROM farmers
WHERE email = 'tj123@gmail.com';

SELECT farmer_id, email, LENGTH(password_hash)
FROM farmers
WHERE email = 'tj123@gmail.com';

USE smart_agriculture_db;

INSERT INTO farms (farmer_id, farm_name, district)
VALUES (5, 'Taizol Farm', 'Dhaka');
SELECT farm_id, farm_name, farmer_id
FROM farms;

SELECT
    fields.field_id,
    fields.field_name,
    fields.farm_id,
    farms.farmer_id
FROM fields
INNER JOIN farms
ON fields.farm_id = farms.farm_id;

INSERT INTO fields
(farm_id, field_name, area_acres, soil_type, soil_ph)
VALUES
(2, 'Taizol Field', 2.50, 'Loamy', 6.50);

SELECT
    fields.field_id,
    fields.field_name,
    fields.farm_id,
    farms.farmer_id
FROM fields
INNER JOIN farms
ON fields.farm_id = farms.farm_id;

USE smart_agriculture_db;

SELECT
    fields.field_id,
    fields.field_name,
    fields.farm_id,
    farms.farm_name,
    farms.farmer_id
FROM fields
INNER JOIN farms
ON fields.farm_id = farms.farm_id
ORDER BY fields.field_id;

USE smart_agriculture_db;

SHOW TABLES;

DESCRIBE planting_cycles;


#farmer activities:

USE smart_agriculture_db;

CREATE TABLE IF NOT EXISTS farming_activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    cycle_id INT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_date DATE NOT NULL,
    description TEXT,
    cost DECIMAL(10,2) DEFAULT 0.00,

    FOREIGN KEY (cycle_id)
        REFERENCES planting_cycles(cycle_id),

    CHECK (cost >= 0)
);
SHOW TABLES;

DESCRIBE farming_activities;

