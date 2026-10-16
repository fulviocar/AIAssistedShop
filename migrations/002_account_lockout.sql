-- Apply once to an existing SQLite database after making a backup.
ALTER TABLE customers ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE customers ADD COLUMN locked_until DATETIME NULL;
