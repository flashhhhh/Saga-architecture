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

CREATE TABLE transaction_history (
    id SERIAL PRIMARY KEY,
    sender_bank_number VARCHAR(20) NOT NULL,
    receiver_bank_number VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL
);

GRANT ALL PRIVILEGES ON TABLE transaction_history TO payment_user;
GRANT USAGE, SELECT ON SEQUENCE transaction_history_id_seq TO payment_user;