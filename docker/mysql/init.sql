CREATE TABLE guitars (
    id VARCHAR(255) PRIMARY KEY,
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    type VARCHAR(255)
);

INSERT INTO guitars (id, make, model, type) VALUES ('b7337fa5-3e17-4628-b4db-00af02e07fdc', 'rickenbacker', '330', 'semi-hollow-electric');
