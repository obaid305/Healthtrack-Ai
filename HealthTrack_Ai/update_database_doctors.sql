-- Add doctor authentication fields
ALTER TABLE doctors ADD COLUMN email VARCHAR(100) UNIQUE;
ALTER TABLE doctors ADD COLUMN password_hash VARCHAR(255);
ALTER TABLE doctors ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE doctors ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE doctors ADD COLUMN last_login TIMESTAMP NULL;

-- Update existing doctors with default login credentials
UPDATE doctors SET email = CONCAT(LOWER(REPLACE(name, ' ', '.')), '@healthtrack.com');
UPDATE doctors SET password_hash = '$2b$12$9tqX9yZzVxL9yX9yZzVxL9yX9yZzVxL9yX9yZzVxL9yX9yZzVxL9yX9yZzV';