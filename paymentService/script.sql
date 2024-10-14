CREATE DATABASE payment_db;
\c payment_db;

CREATE USER payment_user WITH PASSWORD '12345678';

CREATE TABLE bank_accounts (
    bank_number VARCHAR(20) PRIMARY KEY,
    balance DECIMAL(10, 2) NOT NULL
);

GRANT ALL PRIVILEGES ON TABLE bank_accounts TO payment_user;

INSERT INTO bank_accounts (bank_number, balance) VALUES ('0123456789', 1000.00);
INSERT INTO bank_accounts (bank_number, balance) VALUES ('0987654321', 1000.00);