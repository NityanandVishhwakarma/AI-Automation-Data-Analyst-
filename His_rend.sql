CREATE DATABASE exam_analytics;
USE exam_analytics;
CREATE TABLE historical_trends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_year INT NOT NULL,
    exam_stage VARCHAR(50) NOT NULL, -- Prelims, Mains, Interview
    category VARCHAR(50),            -- General, OBC, SC, ST etc.
    cut_off_marks DECIMAL(5,2),
    total_vacancies INT,
    difficulty_level VARCHAR(50)     -- Easy, Moderate, Tough
);