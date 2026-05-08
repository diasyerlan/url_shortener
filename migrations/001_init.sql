CREATE TABLE
    IF NOT EXISTS urls (
        id SERIAL PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        long_url TEXT NOT NULL,
        clicks INT DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW ()
    );

CREATE TABLE IF NOT EXISTS redirect_logs (
    id         BIGSERIAL PRIMARY KEY,
    url_code   TEXT NOT NULL REFERENCES urls(code) ON DELETE CASCADE,
    clicked_at TIMESTAMPTZ DEFAULT NOW(),
    ip         TEXT,
    user_agent TEXT,
    referer    TEXT,
    browser    TEXT,
    os         TEXT,
    device     TEXT
);

CREATE INDEX IF NOT EXISTS idx_logs_code_time
    ON redirect_logs (url_code, clicked_at DESC);