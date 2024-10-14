CREATE DATABASE order_db;
\c order_db;

CREATE USER order_user WITH PASSWORD '12345678';

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    list_of_items TEXT NOT NULL,
    total INT NOT NULL
);

GRANT ALL PRIVILEGES ON TABLE orders TO order_user;