CREATE SCHEMA instruments;

CREATE TABLE instruments.guitars (
    id UUID PRIMARY KEY,
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    type VARCHAR(255),
    source VARCHAR(255) NOT NULL
);

INSERT INTO instruments.guitars (id, make, model, type, source) VALUES
('b7337fa5-3e17-4628-b4db-00af02e07fdc', 'rickenbacker', '330', 'semi-hollow-electric', 'init'),
('54b3e7f2-9d1d-4579-a35e-cbf1aaa5e651', 'fender', 'jazzmaster', 'electric', 'init'),
('c17c9025-ab0e-4adc-b99a-f4ff5a60ff9d', 'fender', 'mustang', 'bass', 'init');
