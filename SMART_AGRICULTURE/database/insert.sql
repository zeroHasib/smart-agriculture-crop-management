USE smart_agriculture_db;

DESCRIBE farms;
DESCRIBE fields;
DESCRIBE crops;
DESCRIBE planting_cycles;
DESCRIBE expenses;

USE smart_agriculture_db;

DESCRIBE farms;
DESCRIBE fields;
DESCRIBE crops;
DESCRIBE planting_cycles;

DESCRIBE farms;
DESCRIBE fields;
DESCRIBE crops;

DESCRIBE farms;
DESCRIBE fields;

DESCRIBE farms;

SELECT * FROM farms
WHERE farmer_id = 6;
SELECT * FROM farms
WHERE farmer_id = 5;

SELECT * FROM farms
WHERE farmer_id = 6;

INSERT INTO farms
(farmer_id, farm_name, district, latitude, longitude)
VALUES
(6, 'Abid Smart Farm', 'Cumilla', 23.4607, 91.1809);

SELECT * FROM farms
WHERE farmer_id = 6;

DESCRIBE expenses;

SELECT
    expense_id,
    expense_type,
    expense_date,
    amount
FROM expenses
ORDER BY expense_date DESC;