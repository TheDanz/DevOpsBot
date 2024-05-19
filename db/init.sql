select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255)
);  
INSERT INTO emails(mail) VALUES ('ryumin.danmil01@mail.ru'), ('ignasheva@yamdex.ru');

CREATE TABLE phone_numbers (
    id SERIAL PRIMARY KEY,
    number VARCHAR(255)
);
INSERT INTO phones(phone) VALUES ('89210650228'), ('+7(981)1239383');