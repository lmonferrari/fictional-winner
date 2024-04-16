CREATE TABLE IF NOT EXISTS education_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

INSERT INTO education_levels (name) VALUES
('Less than a Bachelors'),
('Bachelor’s degree'),
('Master’s degree'),
("Post grad");
