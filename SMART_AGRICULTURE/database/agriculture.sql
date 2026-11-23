
CREATE DATABASE IF NOT EXISTS smart_agriculture_db;

USE smart_agriculture_db;

CREATE TABLE farmers (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE farms (
    farm_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    farm_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),

    FOREIGN KEY (farmer_id)
    REFERENCES farmers(farmer_id)
    ON DELETE CASCADE
);

CREATE TABLE fields (
    field_id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    area_acres DECIMAL(10,2) NOT NULL,
    soil_type VARCHAR(50),
    soil_ph DECIMAL(4,2),

    FOREIGN KEY (farm_id)
    REFERENCES farms(farm_id)
    ON DELETE CASCADE,

    CHECK (area_acres > 0),
    CHECK (soil_ph IS NULL OR soil_ph BETWEEN 0 AND 14)
);

CREATE TABLE crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    growing_duration_days INT,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT IGNORE INTO crops
(crop_name, category, description)
VALUES
('Rice', 'Cereal', 'Rice crop information'),
('Wheat', 'Cereal', 'Wheat crop information'),
('Mustard', 'Oilseed', 'Mustard crop information'),
('Potato', 'Vegetable', 'Potato crop information');
