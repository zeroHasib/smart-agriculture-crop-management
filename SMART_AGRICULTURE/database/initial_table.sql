CREATE DATABASE smart_asset_db;

USE smart_asset_db;

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DOUBLE NOT NULL,
    status VARCHAR(30) NOT NULL
);
