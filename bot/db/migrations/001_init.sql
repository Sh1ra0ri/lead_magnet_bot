CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    added_by BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE lead_magnets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TYPE content_type AS ENUM ('text', 'photo', 'video', 'document', 'audio', 'voice');

CREATE TABLE lead_magnet_messages (
    id SERIAL PRIMARY KEY,
    lead_magnet_id INTEGER NOT NULL REFERENCES lead_magnets(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    content_type content_type NOT NULL,
    text TEXT,
    file_id VARCHAR(255),
    buttons JSONB
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT now()
);